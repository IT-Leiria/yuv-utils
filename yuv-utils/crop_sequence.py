import argparse
import os

import matplotlib.pyplot as plt
import numpy as np
import tqdm as tqdm


def crop_frame(frame, x: int, y: int, w: int, h: int):
    return frame[y:y+h, x:x+w]


def __test__(input: str, width: int, height: int):
    total_frames = os.path.getsize(input) // (width * height * 3 // 2)

    # Frame Loop
    for fi in range(total_frames):
        with open(input, "rb") as freader:
            # Move file pointer
            freader.seek(fi * width * height * 3 // 2)
            b_ref_y = freader.read(width * height)
            ref_y = np.frombuffer(b_ref_y, dtype=np.uint8).reshape((height, width))
            b_ref_u = freader.read(width // 2 * height // 2)
            ref_u = np.frombuffer(b_ref_u, dtype=np.uint8).reshape((height // 2, width // 2))
            b_ref_v = freader.read(width // 2 * height // 2)
            ref_v = np.frombuffer(b_ref_v, dtype=np.uint8).reshape((height // 2, width // 2))

        plt.imshow(ref_y, cmap="gray")
        plt.show()
        plt.imshow(ref_u, cmap="gray")
        plt.show()
        plt.imshow(ref_v, cmap="gray")
        plt.show()

        crop_y = crop_frame(ref_y, 0, 0, width, height)
        crop_u = crop_frame(ref_u, 0 // 2, 0 // 2, width // 2, height // 2)
        crop_v = crop_frame(ref_v, 0 // 2, 0 // 2, width // 2, height // 2)

        plt.imshow(crop_y, cmap="gray")
        plt.show()
        plt.imshow(crop_u, cmap="gray")
        plt.show()
        plt.imshow(crop_v, cmap="gray")
        plt.show()

        b_crop_y = crop_y.ravel().tobytes()
        if b_ref_y != b_crop_y:
            raise ValueError("")
        b_crop_u = crop_u.ravel().tobytes()
        if b_ref_u != b_crop_u:
            raise ValueError("")
        b_crop_v = crop_v.ravel().tobytes()
        if b_ref_v != b_crop_v:
            raise ValueError("")


def main(
        input: str, width: int, height: int,
        x: int, y: int, w: int, h: int,
        output: str = None,
        max_frames: int = None, first_frame: int = None,
        verbose: bool = False
):
    # Get the total frames of the input file
    total_frames = os.path.getsize(input) // (width * height * 3 // 2)

    # Sets the number of frames to be cropped
    if max_frames is None:
        max_frames = total_frames - 1   # Index mode
    if max_frames > total_frames:
        max_frames = total_frames - 1   # Index mode

    # Sets the first frame
    if first_frame is None:
        first_frame = 0
    if first_frame < 0:
        first_frame = 0
    if first_frame > max_frames:
        first_frame = max_frames

    # Builds the output file name if this is not provided
    if output is None:
        output = os.path.splitext(input)[0] + f"-crop{x}:{y}.{w}x{h}.yuv"

    # Remove file before appended
    if os.path.isfile(output):
        os.remove(output)

    # Frames iterator (with or without progress bar)
    if verbose:
        iterator = tqdm.tqdm(range(first_frame, max_frames), desc="Cropping frames")
    else:
        iterator = range(first_frame, max_frames)

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

        # Crop luma, chroma U and chroma V
        crop_y = crop_frame(ref_y, x, y, w, h)
        crop_u = crop_frame(ref_u, x // 2, y // 2, w // 2, h // 2)
        crop_v = crop_frame(ref_v, x // 2, y // 2, w // 2, h // 2)

        # Save/append the cropped frame to file
        with open(output, "ab") as fwriter:
            # Move file pointer
            fwriter.write(crop_y.ravel().tobytes())
            fwriter.write(crop_u.ravel().tobytes())
            fwriter.write(crop_v.ravel().tobytes())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Frame-wise cropping of an YUV video based on rectangle defined by x,y,w and h. CURRENTLY THIS TOOL ONLY SUPPORTS YUV420P FORMAT."
    )
    parser.add_argument("input", type=str, help="Path to the video to be cropped.")
    parser.add_argument("width", type=int, help="Width of the video to be cropped.")
    parser.add_argument("height", type=int, help="Height of the video to be cropped.")
    parser.add_argument("x", type=int, help="Width of the video to be cropped.")
    parser.add_argument("y", type=int, help="Height of the video to be cropped.")
    parser.add_argument("w", type=int, help="Width of the video to be cropped.")
    parser.add_argument("h", type=int, help="Height of the video to be cropped.")
    parser.add_argument(
        "-o", "--output", default=None, type=str,
        help="Path to the cropped video. Defaults to the input path with `-crop<x>:<y>.<w>x<h>.yuv` appended."
    )
    parser.add_argument(
        "-m", "--max_frames", default=None, type=int,
        help="Sets the number of frames to be cropped. Defaults to the total frames of input video."
    )
    parser.add_argument(
        "-f", "--first_frame", default=None, type=int,
        help="Sets the starting frame to be cropped. Defaults to the first frame of the input video."
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
        x=args.x,
        y=args.y,
        w=args.w,
        h=args.h,
        output=args.output,
        first_frame=args.first_frame,
        max_frames=args.max_frames,
        verbose=args.verbose
    )