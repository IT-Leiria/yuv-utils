import numpy as np

from scipy.ndimage import zoom

class YUV:
    def __init__(self, filename, size,num_bit):
        self.height, self.width = size
        self.frame_len_luma = int((self.width * self.height*np.ceil(num_bit/8)))
        self.frame_len_chroma = int((self.width * self.height*np.ceil(num_bit/8))//4)
        self.f = open(filename, 'rb')
        self.shape_luma = (int(self.width), int(self.height))
        self.shape_chroma = (int(self.width/2), int(self.height/2))
        self.num_bits = num_bit
 
    def __read_raw(self):
        try:
            if self.num_bits==8:
                dtipo= np.uint8
            elif self.num_bits==10 or self.num_bits==16:
                dtipo= np.uint16
            raw = self.f.read(self.frame_len_luma)
            y = np.frombuffer(raw, dtype=dtipo).reshape(self.shape_luma)
            raw = self.f.read(self.frame_len_chroma)
            u = np.frombuffer(raw, dtype=dtipo).reshape(self.shape_chroma)
            raw = self.f.read(self.frame_len_chroma)
            v = np.frombuffer(raw, dtype=dtipo).reshape(self.shape_chroma)
            u = zoom(u, self.shape_luma[0]/self.shape_chroma[0])
            v = zoom(v, self.shape_luma[0]/self.shape_chroma[0])
            if self.num_bits==10 or self.num_bits==16:
                y = y/(2^self.num_bits)
                u = u/(2^self.num_bits)
                v = v/(2^self.num_bits)
                # yuv = np.uint8(cv2.merge((y, u, v))*255)
            yuv = np.uint8(np.stack([y, u, v], axis=2))

        except Exception as e:
            print(str(e))
            return False, None
        return True, yuv
 
    def read(self):
        ret, yuv = self.read_raw()
        if not ret:
            return ret, yuv
        # bgr = cv2.cvtColor(yuv, cv2.COLOR_lumaCrCb2RGB)#cv2.COLOR_lumaUV2BGR_NV21)
        # return ret, bgr
        return yuv

