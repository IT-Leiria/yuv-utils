import argparse
import os

import numpy as np
import tqdm as tqdm


def main(
        input: str, width: int, height: int,
        output: str = None,
        last_frame: int = None, first_frame: int = None,
        verbose: bool = False
):
    # Get the total frames of the input file
    total_frames = os.path.getsize(input) // (width * height * 3 // 2)

    # Sets the number of frames to be cropped
    if last_frame is None:
        last_frame = total_frames - 1   # Index mode
    if last_frame > total_frames:
        last_frame = total_frames - 1   # Index mode

    # Sets the first frame
    if first_frame is None:
        first_frame = 0
    if first_frame < 0:
        first_frame = 0
    if first_frame > last_frame:
        first_frame = last_frame

    # Builds the output file name if this is not provided
    if output is None:
        output = os.path.splitext(input)[0] + f"-[{first_frame},{last_frame}].yuv"

    # Remove file before appended
    if os.path.isfile(output):
        os.remove(output)

    # Frames iterator (with or without progress bar)
    if verbose:
        iterator = tqdm.tqdm(range(first_frame, last_frame + 1), desc="Extracting frames")
    else:
        iterator = range(first_frame, last_frame + 1)

    # Frame Loop
    for fi in iterator:
        # Read frame i of the input
        with open(input, "rb") as freader:
            # Move file pointer
            freader.seek(fi * width * height * 3 // 2)
            # Read luma
            ref_y = np.frombuffer(freader.read(width * height), dtype=np.uint8).reshape((height, width))
            # Read chroma U and V
            ref_u = np.frombuffer(freader.read(width//2 * height//2), dtype=np.uint8).reshape((height//2, width//2))
            ref_v = np.frombuffer(freader.read(width // 2 * height // 2), dtype=np.uint8).reshape((height//2, width//2))

        # Save/append the cropped frame to file
        with open(output, "ab") as fwriter:
            # Move file pointer
            fwriter.write(ref_y.ravel().tobytes())
            fwriter.write(ref_u.ravel().tobytes())
            fwriter.write(ref_v.ravel().tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extracts frames from an YUV sequence, i.e. trims/chops an YUV sequence. CURRENTLY THIS TOOL ONLY SUPPORTS YUV420P FORMAT."
    )
    parser.add_argument("input", type=str, help="Path to the video to be trimmed.")
    parser.add_argument("width", type=int, help="Width of the video to be trimmed.")
    parser.add_argument("height", type=int, help="Height of the video to be trimmed.")
    parser.add_argument(
        "-o", "--output", default=None, type=str,
        help="Path to the cropped video. Defaults to the input path with `-[<initial frame>, <last frame>].yuv` "
             "appended."
    )
    parser.add_argument(
        "-f", "--first_frame", default=None, type=int,
        help="Sets the starting frame. Defaults to the first frame of the input video."
    )
    parser.add_argument(
        "-l", "--last_frame", default=None, type=int,
        help="Sets the last frame (non inclusive). Defaults to the total frames of input video."
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
        first_frame=args.first_frame,
        last_frame=args.last_frame,
        verbose=args.verbose
    )
