import numpy as np, colorsys
from PIL import Image, ImageFilter
src=Image.open(__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'sethrak_diamondback.png').convert('RGBA')
A=np.asarray(src).astype(np.float32)/255
rgb,alpha=A[...,:3],A[...,3]
hsv=np.asarray(src.convert('RGB').convert('HSV')).astype(np.float32)/255
H,S,V=hsv[...,0]*360,hsv[...,1],hsv[...,2]
lum=(rgb@np.array([0.299,0.587,0.114],np.float32))
yy,xx=np.mgrid[0:512,0:512]
def blur(m,r): return np.asarray(Image.fromarray((np.clip(m,0,1)*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r))).astype(np.float32)/255
# glow stripes: cyan hue, plus their bright cores (low alpha)
cyan=np.clip((S-0.12)/0.25,0,1)*np.clip(1-np.abs(H-185)/40,0,1)
core=blur(cyan,2.5)*np.clip((V-0.55)/0.3,0,1)
glow=np.clip(np.maximum(cyan,core),0,1)
# eyes: two circles in the UV map, where the alpha is low
eye=np.zeros_like(lum)
for cx,cy,r in ((396,66,15),(296,215,15)):
    d=np.sqrt((xx-cx)**2+(yy-cy)**2)
    eye=np.maximum(eye,np.clip((r-d)/4,0,1)*np.clip((0.85-alpha)/0.3,0,1))
eye=blur(eye,1.0)
glow=glow*(1-eye)
def tint(img,color,amount):
    c=np.array(color,np.float32)/255
    l=img@np.array([0.299,0.587,0.114],np.float32)
    cl=c@np.array([0.299,0.587,0.114],np.float32)
    t=c*(l/max(cl,1e-3))[...,None] if False else c[None,None,:]*(l[...,None]/cl)
    return img*(1-amount)+np.clip(t,0,1)*amount
def recolor(glow_rgb,eye_rgb,dark_rgb,light_rgb,body_amt):
    out=rgb.copy()
    # body: a two-tone gradient map (dark pattern -> dark_rgb, light scales -> light_rgb), blended in lightly
    d=np.array(dark_rgb,np.float32)/255; lt=np.array(light_rgb,np.float32)/255
    t=np.clip((lum-0.15)/0.6,0,1)[...,None]
    gm=(d*(1-t)+lt*t)
    gl=gm@np.array([0.299,0.587,0.114],np.float32)
    gm=np.clip(gm*(lum/np.maximum(gl,1e-3))[...,None],0,1)
    out=out*(1-body_amt)+gm*body_amt
    # glow and eyes: new hue, same brightness shape (white cores stay bright)
    g=np.array(glow_rgb,np.float32)/255
    gcol=np.clip(g*(V[...,None]*1.25)+ (np.clip(V-0.8,0,1)[...,None]*1.2),0,1)
    out=out*(1-glow[...,None])+gcol*glow[...,None]
    e=np.array(eye_rgb,np.float32)/255
    ecol=np.clip(e*(0.35+1.1*lum[...,None])+np.clip(lum-0.7,0,1)[...,None],0,1)
    out=out*(1-eye[...,None])+ecol*eye[...,None]
    return Image.fromarray((np.dstack([out,alpha])*255+0.5).clip(0,255).astype(np.uint8),'RGBA')
SKINS={
 # name: glow, eyes, pattern dark, scale light, body amount
 'ember':    ((255,110,30),(255,150,20),(110,35,20),(215,160,110),0.35),
 'viper':    ((110,255,60),(190,255,40),(40,75,25),(170,190,120),0.35),
 'dusk':     ((185,90,255),(230,120,255),(55,35,80),(175,165,190),0.35),
 'gilded':   ((255,210,70),(255,225,90),(95,70,20),(235,210,150),0.30),
 'blood':    ((255,40,50),(255,60,40),(80,15,20),(190,130,115),0.40),
}
if __name__=='__main__':
    Image.fromarray((glow*255).astype(np.uint8)).save('glowmask.png')
    Image.fromarray((eye*255).astype(np.uint8)).save('eyemask.png')
    for k,v in SKINS.items(): recolor(*v).save(f'sethrak_devourer_{k}.png')
