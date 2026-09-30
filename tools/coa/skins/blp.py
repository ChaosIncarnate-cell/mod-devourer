import struct, io, sys
from PIL import Image
def dxt5(img):
    b=io.BytesIO(); img.save(b,'DDS',pixel_format='DXT5'); d=b.getvalue()
    assert d[:4]==b'DDS ' and d[84:88]==b'DXT5', d[84:88]
    return d[128:]
def write_blp(img,path):
    img=img.convert('RGBA'); w,h=img.size; mips=[]
    while True:
        mips.append(dxt5(img if img.size==(w,h) and not mips else img))
        if img.size==(1,1): break
        img=img.resize((max(1,img.size[0]//2),max(1,img.size[1]//2)),Image.LANCZOS)
    offs=[];sizes=[];pos=20+64+64+1024
    for m in mips: offs.append(pos); sizes.append(len(m)); pos+=len(m)
    offs+= [0]*(16-len(offs)); sizes+=[0]*(16-len(sizes))
    hdr=b'BLP2'+struct.pack('<I4B2I',1,2,8,7,1,w,h)+struct.pack('<16I',*offs)+struct.pack('<16I',*sizes)+b'\0'*1024
    open(path,'wb').write(hdr+b''.join(mips))
if __name__=='__main__':
    write_blp(Image.open(sys.argv[1]),sys.argv[2])
