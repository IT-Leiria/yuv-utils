import argparse
import os

import numpy as np
import tqdm as tqdm


def main(
        input: str, width: int, height: int,
        output: str = None,
        max_frames: int = None,
        verbose: bool = False
):
    # Builds the output file name if this is not provided
    if output is None:
        output = os.path.splitext(input)[0] + f"-frames{max_frames}.yuv"

    # Remove file before appended
    if os.path.isfile(output):
        os.remove(output)

    # Frames iterator (with or without progress bar)
    if verbose:
        iterator = tqdm.tqdm(range(0, max_frames), desc="Duplicating frames")
    else:
        iterator = range(0, max_frames)

    with open(input, "rb") as freader:
        # Read luma
        ref_y = np.frombuffer(freader.read(width * height), dtype=np.uint8).reshape((height, width))
        # Read chroma U and V
        ref_u = np.frombuffer(freader.read(width // 2 * height // 2), dtype=np.uint8).reshape((height // 2, width // 2))
        ref_v = np.frombuffer(freader.read(width // 2 * height // 2), dtype=np.uint8).reshape((height // 2, width // 2))

    # Frame Loop
    for fi in iterator:
        # Save/append the cropped frame to file
        with open(output, "ab") as fwriter:
            # Move file pointer
            fwriter.write(ref_y.ravel().tobytes())
            fwriter.write(ref_u.ravel().tobytes())
            fwriter.write(ref_v.ravel().tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Duplicates a frame throughout an YUV sequence. CURRENTLY THIS TOOL ONLY SUPPORTS YUV420P FORMAT."
    )
    parser.add_argument("input", type=str, help="Path to the frame to be duplicated/collated.")
    parser.add_argument("width", type=int, help="Width of the frame to be duplicated/collated.")
    parser.add_argument("height", type=int, help="Height of the frame to be duplicated/collated.")
    parser.add_argument("max_frames", type=int, help="Sets the length of the YUV sequence, i.e., the number of frame "
                                                     "duplications.")
    parser.add_argument(
        "-o", "--output", default=None, type=str,
        help="Path to the cropped video. Defaults to the input path with `-frames<number of frames>.yuv` appended."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true",
        help="Prints current status. Defaults to False."
    )
    args = parser.parse_args()

    args.input = os.path.expanduser(os.path.normpath(args.input))
    if args.output is not None:
        args.output = os.path.expanduser(os.path.normpath(args.output))

    main(
        input=args.input,
        width=args.width,
        height=args.height,
        output=args.output,
        max_frames=args.max_frames,
        verbose=args.verbose
    )
