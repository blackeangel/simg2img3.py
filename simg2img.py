import os
import sys
import struct
EXT4_HEADER_MAGIC = 0xED26FF3A
EXT4_CHUNK_HEADER_SIZE = 12
EXT4_CHUNK_HEADER_SIZE_PANIC = 16
 
 
class ext4_file_header(object):
    def __init__(self, buf):
        (self.magic,
         self.major,
         self.minor,
         self.file_header_size,
         self.chunk_header_size,
         self.block_size,
         self.total_blocks,
         self.total_chunks,
         self.crc32) = struct.unpack('<I4H4I', buf)
#< - обратный порядок
 
#H - беззнаковое короткое целое число, 2 байта
#I - беззнаковое целое число, 4 байта
class ext4_chunk_header_normal(object):
    def __init__(self, buf):
        (self.type,
         self.reserved,
         self.chunk_size,
         self.total_size) = struct.unpack('<2H2I', buf)
 
class ext4_chunk_header_epic(object):
    def __init__(self, buf):
        (self.type,
         self.reserved,
         self.chunk_size,
         self.total_size) = struct.unpack('<4x2H2I', buf)
 
class Converter(object):
    def __converSimgToImg(self, target):
        with open(target, "rb") as img_file:
            header = ext4_file_header(img_file.read(28))
            print('header = '+ header.__str__())
            total_chunks = header.total_chunks
            print('total_chunks = '+total_chunks.__str__())
            with open(target.replace(".img", ".raw.img"), "wb") as raw_img_file:
                sector_base = 82528
                output_len = 0
                while total_chunks > 0:
                    if header.file_header_size == 32:
                        chunk_header = ext4_chunk_header_epic(img_file.read(EXT4_CHUNK_HEADER_SIZE_PANIC))
                    else:
                        chunk_header = ext4_chunk_header_normal(img_file.read(EXT4_CHUNK_HEADER_SIZE))
                    sector_size = (chunk_header.chunk_size * header.block_size) >> 9
                    print('sector_size2 =' + hex(chunk_header.chunk_size * header.block_size).__str__())
                    print('sector_size =' + hex(sector_size).__str__())
                    print('chunk_header =' + chunk_header.__str__())
                    print('chunk_header.type =' + chunk_header.type.__str__())
                    if chunk_header.type == 0xCAC1:
                        if header.file_header_size == 32:
                            data = img_file.read(chunk_header.total_size - EXT4_CHUNK_HEADER_SIZE_PANIC)
                        else:
                            data = img_file.read(chunk_header.total_size - EXT4_CHUNK_HEADER_SIZE)
                        len_data = len(data)
                        print('len_data_0xCAC1 =' + len_data.__str__())
                        if len_data != (sector_size << 9):
                            pass
                        else:
                            raw_img_file.write(data)
                    else:
                        len_data = sector_size << 9 #сдвиг на 9 бит влево.. интересно что за глупость там?
                        print('len_data=' + len_data.__str__())
                        print('struct.pack("B", 0)='+ struct.pack("B", 0).__str__())
 #                       print('print(struct.pack("B", 0) * len_data)='+ (struct.pack("B", 0) * len_data).__str__())
                        raw_img_file.write(struct.pack("B", 0) * len_data)
 
                    output_len += len_data
                    sector_base += sector_size
                    total_chunks -= 1
                    print('______________________________________________________________')
        self.OUTPUT_IMAGE_FILE = target.replace(".img", ".raw.img")
 
    def __getTypeTarget(self, target):
        filename, file_extension = os.path.splitext(target)
        if file_extension == '.img':
            with open(target, "rb") as img_file:
                header = ext4_file_header(img_file.read(28))
                if header.magic != EXT4_HEADER_MAGIC:
                    return 'img'
                else:
                    return 'simg'
 
    def main(self, target):
        target_type = self.__getTypeTarget(target)
        if target_type == 'simg':
            print("Convert %s to %s" % (os.path.basename(target), os.path.basename(target).replace(".img", ".raw.img")))
            self.__converSimgToImg(target)
Converter().main(sys.argv[1])