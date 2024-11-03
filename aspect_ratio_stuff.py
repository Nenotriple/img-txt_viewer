import re
from fractions import Fraction

parsing_regex = re.compile(r"x|:")

#region Interface Functions
def get_optimal_crop_dimensions(input_resolution: str, aspect_ratios: list[str], tolerance: float):
    """Return a dictionary of optimal crop dimensions for each aspect ratio in a list of aspect ratio strings for a given input_resolution string.\n
    Tolerance is the allowable delta from the aspect scalar."""
    optimal_dict = {target_aspect_ratio: optimal_crop_resolution(input_resolution, target_aspect_ratio, tolerance) for target_aspect_ratio in aspect_ratios}
    return optimal_dict


def get_area_preserving_dimensions(input_resolution: str, aspect_ratios: list[str]):
    """Return a dictionary of area preserving dimensions for each aspect ratio in a list of aspect ratio strings for a given input_resolution string."""
    area_dict = {target_aspect_ratio: preserved_area_resolution(input_resolution, target_aspect_ratio) for target_aspect_ratio in aspect_ratios}
    return area_dict


#endregion
#region Scaling Algorithms
def optimal_crop_resolution(
        input_resolution,
        target_aspect_ratio,
        tolerance: float = 0.0,
        multiple_of: int = 64,
        quiet: bool = False
        ):
    """
    Find the target dimensions (adjusted_width, adjusted_height) with an aspect ratio within
    tolerance of target_aspect_ratio and where each dimension is the nearest multiple of 64 and less
    than or equal to their respective input resolution dimensions (original_width, original_height).
    """
    original_width, original_height = parse_string(input_resolution)
    target_aspect_numerator, target_aspect_denominator = parse_string(target_aspect_ratio)
    if target_aspect_numerator <= 0 or target_aspect_denominator <= 0 or original_width <= 0 or original_height <= 0:
        raise ValueError("Height, width, aspect_numerator and aspect denominator must each be greater than zero.")
    MAX_NUMBER_OF_BACK_PROPAGATIONS = 10 # When adjusted dimensions ratio falls out of tolerance, iteratively downsize by 64 this many times until a tolerable resolution is found. If not found, returns the result with lowest delta.
    ratio_original = original_width / original_height
    ratio_target = target_aspect_numerator / target_aspect_denominator
    ratio_min = ratio_target - tolerance
    ratio_max = ratio_target + tolerance
    # Check if current aspect ratio is already within the acceptable range
    if ratio_min <= ratio_original <= ratio_max:
        adjusted_width = original_width
        adjusted_height = original_height
    else:
        diff_min = abs(ratio_original - ratio_min)
        diff_max = abs(ratio_original - ratio_max)
        # Choose ratio closest to ratio_original
        if diff_min <= diff_max:
            ratio_prime = ratio_min
        else:
            ratio_prime = ratio_max
        # Adjust dimensions based on ratio_prime and ensure they are less than or equal to original dimensions
        if ratio_prime >= ratio_original:
            # Adjust height
            adjusted_width = original_width
            adjusted_height = adjusted_width // ratio_prime
            if adjusted_height > original_height:
                adjusted_height = original_height
                adjusted_width = ((adjusted_height * ratio_prime) // multiple_of) * multiple_of
        else:
            # Adjust width
            adjusted_height = original_height
            adjusted_width = ((adjusted_height * ratio_prime) // multiple_of) * multiple_of
            if adjusted_width > original_width:
                adjusted_width = original_width
                adjusted_height = adjusted_width // ratio_prime
    # Adjust dimensions again to be multiples of 64 for latent compatibility
    adjusted_width, adjusted_height = adjust_resolution_to_latent_analogue((adjusted_width, adjusted_height), multiple_of)
    # Ensure adjusted dimensions are less than or equal to original dimensions
    adjusted_width = min(original_width, adjusted_width)
    adjusted_height = min(original_height, adjusted_height)
    # Verify the adjusted aspect ratio is within tolerance
    adjusted_ratio = adjusted_width / adjusted_height
    fallback_flag = True
    result_history = []
    if not (ratio_min <= adjusted_ratio <= ratio_max):
        # Try adjusting dimensions to satisfy aspect ratio within tolerance
        # Since dimensions must be multiples of 'multiple_of', we can adjust further
        if adjusted_ratio < ratio_min:
            # Adjust width
            range_length = adjusted_width // multiple_of
            range_limit = max(range_length - MAX_NUMBER_OF_BACK_PROPAGATIONS, 0)
            for w_multiplier in range(range_length, range_limit, -1):
                possible_width = w_multiplier * multiple_of
                possible_height = possible_width / ratio_prime
                possible_height = round(possible_height / multiple_of) * multiple_of
                if possible_height <= adjusted_height and possible_height > 0:
                    adjusted_width = possible_width
                    adjusted_height = possible_height
                    adjusted_ratio = adjusted_width / adjusted_height
                    if ratio_min <= adjusted_ratio <= ratio_max:
                        fallback_flag = False
                        break
                    result_history.append((possible_width, possible_height, a := round(adjusted_ratio, 4), a - round(ratio_target, 4)))
        else:
            # Adjust height
            range_length = adjusted_height // multiple_of
            range_limit = max(range_length - MAX_NUMBER_OF_BACK_PROPAGATIONS, 0)
            for h_multiplier in range(range_length, range_limit, -1):
                possible_height = h_multiplier * multiple_of
                possible_width = possible_height * ratio_prime
                possible_width = round(possible_width / multiple_of) * multiple_of
                if possible_width <= adjusted_width and possible_width > 0:
                    adjusted_width = possible_width
                    adjusted_height = possible_height
                    adjusted_ratio = adjusted_width / adjusted_height
                    if ratio_min <= adjusted_ratio <= ratio_max:
                        fallback_flag = False
                        break
                    result_history.append((possible_width, possible_height, a := round(adjusted_ratio, 4), a - round(ratio_target, 4)))

        if fallback_flag:
            if not len(result_history):
                print(f"Something went terribly wrong. Could not find compatible resolution at all.")
                return 0, 0
            result_history.sort(key=lambda x: abs(x[3]))
            adjusted_width, adjusted_height, adjusted_ratio, tolerance_delta = result_history[0]
            if not quiet:
                result_aspect_ratio = Fraction(adjusted_ratio).limit_denominator(100)
                print(f"""Input res:\t{original_width}, {original_height}\t({target_aspect_ratio}={round(ratio_target, 4)}):\tCannot find latent compatible dimensions that satisfy the aspect ratio within tolerance.
Closest match:\t{adjusted_width}, {adjusted_height}\t({result_aspect_ratio.numerator}:{result_aspect_ratio.denominator}={adjusted_ratio}):\tOutside tolerance range {round(ratio_min, 4)} - {round(ratio_max, 4)}. Delta from optimal ratio {tolerance_delta:1.4f}""")
            #TODO Force into bucket via destructive stretch or crop
            return adjusted_width, adjusted_height

    return adjusted_width, adjusted_height


def preserved_area_resolution(input_resolution_str, target_aspect_ratio):
    """
    Find the target dimensions (adjusted_width, adjusted_height) nearest to the input resolution
    with target_aspect_ratio and where each dimension is the nearest multiple of 64.
    """
    scale_factor = get_linear_scalar(input_resolution_str, target_aspect_ratio)
    x, y = parse_string(target_aspect_ratio)
    scaled_resolution =  x * scale_factor, y * scale_factor
    adjusted_width, adjusted_height = adjust_resolution_to_latent_analogue(scaled_resolution)
    return adjusted_width, adjusted_height


#endregion
#region Helper Functions
def parse_string(input_str: str):
    """Parse an aspect ratio string "1:1" or a resolution string "1024x1024" to a tuple"""
    x, y = map(int, parsing_regex.split(input_str))
    return x, y


def get_scalar(input_str: str):
    """Calculate a scalar from an aspect ratio string "1:1" or a resolution string "1024x1024" """
    x, y = parse_string(input_str)
    return x / y


def get_linear_scalar(input_resolution_str: str, target_aspect_ratio: str):
    """Calculate a linear scalar from an input resolution string "1024x1024" and a target aspect ratio string "1:1" """
    w, h = parse_string(input_resolution_str)
    x, y = parse_string(target_aspect_ratio)
    area = w * h
    adjusted_ratio = x * y
    scale_factor = (area / adjusted_ratio) ** 0.5
    return scale_factor


def adjust_resolution_to_latent_analogue(input_resolution: str|tuple, multiple_of: int = 64):
    """Round the input_resolution string "1024x1024" or tuple (1024, 1024) to the nearest integer multiple given by multiple_of."""
    if isinstance(input_resolution, str):
        input_resolution = parse_string(input_resolution)
    width, height = input_resolution
        # Adjust dimensions again to be multiples of 64 for latent compatibility
    adjusted_width = max((round(width / multiple_of)), 1) * 64
    adjusted_height = max((round(height / multiple_of)), 1) * 64
    return adjusted_width, adjusted_height


def closest_aspect_ratio(resolution: str, aspect_ratios: list[str]):
    """Determine the nearest aspect ratio to the resolution string "1024x1024" from a list of aspect ratio strings ["1:1"]"""
    scalar: float = get_scalar(resolution)
    closest_ratio = None
    smallest_diff = float("inf")
    for aspect_ratio in aspect_ratios:
        diff = abs(scalar - get_scalar(aspect_ratio))
        if diff < smallest_diff:
            smallest_diff = diff
            closest_ratio = aspect_ratio
    return closest_ratio

#endregion
#region Examples
def main():
    print("main()")
    aspect_ratios = ['4:3', '3:4', '16:9', '3:2', '5:8', '1:1']
    input_resolution = "1024x1024"
    tolerance = 0.05
    print("input_resolution:", input_resolution)
    print("closest_aspect_ratio:", closest_aspect_ratio(input_resolution, aspect_ratios))
    optimal_dict = get_optimal_crop_dimensions(input_resolution, aspect_ratios, tolerance)
    print("optimal_crop:", optimal_dict)
    area_dict = get_area_preserving_dimensions(input_resolution, aspect_ratios)
    print("area_preserve:", area_dict)
    print()


def unit_test(target_aspect_ratio='1:1', input_resolution="1024x1024", tolerance=0.0):
    args_str = ', '.join(f"{k}={v!r}" for k, v in locals().items())
    print(f"unit_test({args_str})")
    optimal_res = optimal_crop_resolution(input_resolution, target_aspect_ratio, tolerance)
    print("Result:", optimal_res)
    print()


def benchmark():
    print("benchmark()")
    import timeit
    iterations = 100000
    aspect_ratios = ['4:3', '3:4', '16:9', '3:2', '5:8', '1:1']
    input_resolution = "1024x1024"
    tolerance = 0.0

    # Single value tests: aspect_ratio -> result_dimensions
    optimal_time = timeit.timeit(lambda: optimal_crop_resolution(input_resolution, aspect_ratios[0], tolerance), number=iterations)
    area_preserve_time = timeit.timeit(lambda: preserved_area_resolution(input_resolution, aspect_ratios[0]), number=iterations)
    print(f"Average time to retrieve dimensions for a single optimal aspect: {(t := optimal_time / iterations):.8f} seconds")
    print(f"Average time to retrieve dimensions for a single preserving aspect: {(t := area_preserve_time / iterations):.8f} seconds")
    print()

    # Dictionary tests: aspect_ratios -> dict(aspect_ratio: result_dimensions)
    optimal_dict_time = timeit.timeit(lambda: get_optimal_crop_dimensions(input_resolution, aspect_ratios, tolerance), number=iterations)
    area_preserve_dict_time = timeit.timeit(lambda: get_area_preserving_dimensions(input_resolution, aspect_ratios), number=iterations)
    print(f"Average time to retrieve optimal dictionary: {(t := optimal_dict_time / iterations):.8f} seconds")
    print(f"Average time to retrieve a single aspect from dictionary: {t / len(aspect_ratios):.8f} seconds")
    print(f"Average time to retrieve preserving dictionary: {(t := area_preserve_dict_time / iterations):.8f} seconds")
    print(f"Average time to retrieve a single aspect from dictionary: {t / len(aspect_ratios):.8f} seconds")
    print()


main()
unit_test("4:3", "1025x1002")
unit_test("1:1", "12225x1002")
unit_test("16:9", "1025x1002")
unit_test("2:3", "1025x1002")
unit_test("5436:32", "1025x1002")
unit_test("5436:32", "1500016x10555")
benchmark()