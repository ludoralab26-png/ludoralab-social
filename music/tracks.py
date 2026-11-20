import numpy as np, wave, subprocess
sr=44100
m=lambda x:440*2**((x-69)/12)
def make(name,bpm,chords,mel,T=30,kick=(0,2),melstart=2,pluckdecay=6,seed=1,hatamp=0.05):
    rng=np.random.default_rng(seed); beat=60/bpm; barlen=4*beat
    t=np.arange(int(sr*T))/sr; out=np.zeros_like(t)
    def note(f,start,dur,amp,kind='pad'):
        i0=int(start*sr)
        if i0>=len(out): return
        n=int(dur*sr); tt=np.arange(n)/sr
        if kind=='pad':
            w=sum(np.sin(2*np.pi*f*k*tt+0.3*k)/k for k in (1,2,3))
            env=np.minimum(1,tt/0.4)*np.minimum(1,np.maximum(0,(dur-tt)/0.6))
        elif kind=='pluck':
            w=np.sin(2*np.pi*f*tt)+0.3*np.sin(2*np.pi*2*f*tt); env=np.exp(-tt*pluckdecay)
        elif kind=='kick':
            w=np.sin(2*np.pi*(50+90*np.exp(-tt*30))*tt); env=np.exp(-tt*9)
        else:
            w=rng.standard_normal(n); env=np.exp(-tt*60)
        seg=w*env*amp; j=min(len(out),i0+n); out[i0:j]+=seg[:j-i0]
    b=0
    while b*barlen<T:
        c=chords[b%len(chords)]; s=b*barlen
        for x in c: note(m(x),s,barlen,0.10)
        note(m(c[0]-12),s,barlen,0.12)
        for k in range(4):
            if k in kick: note(0,s+k*beat,0.4,0.5,'kick')
            note(0,s+k*beat+beat/2,0.1,hatamp,'hat'); note(0,s+k*beat,0.1,hatamp*0.6,'hat')
        if b>=melstart:
            for k in range(8):
                x=mel[(k+b*3)%len(mel)]
                if x: note(m(x),s+k*beat/2,0.5,0.12,'pluck')
        b+=1
    out*=np.minimum(1,np.minimum(t/1.0,(T-t)/2.0)); out=out/np.max(np.abs(out))*0.8
    st=np.stack([out,np.roll(out,300)],1)
    with wave.open(f'/tmp/{name}.wav','w') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(sr); f.writeframes((st*32767).astype('<i2').tobytes())
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i',f'/tmp/{name}.wav','-b:a','192k',f'tracks/{name}.mp3'],check=True)
import os; os.makedirs('tracks',exist_ok=True)
# 1 calm: the one you liked (Am F C G)
make('01-calm',96,[[57,60,64],[53,57,60],[48,52,55],[55,59,62]],[69,72,71,67,69,64,65,67])
# 2 bright/uplifting (C G Am F), quicker
make('02-bright',108,[[48,52,55],[55,59,62],[57,60,64],[53,57,60]],[72,76,74,72,79,76,74,71],kick=(0,1,2,3),melstart=1,pluckdecay=8)
# 3 focused/serious (Dm Bb Gm A), slower
make('03-focused',84,[[50,53,57],[46,50,53],[43,46,50],[45,49,52]],[69,0,65,67,0,62,64,0],melstart=2,pluckdecay=4,hatamp=0.035)
# 4 energetic (Em C G D), fast
make('04-energetic',120,[[52,55,59],[48,52,55],[55,59,62],[50,54,57]],[71,74,76,74,71,67,69,71],kick=(0,1,2,3),melstart=1,pluckdecay=10,hatamp=0.06)
# 5 eastern touch: Hijaz-flavored melody over D / Gm / Cm / D (for Arabic posts)
make('05-hijaz',92,[[50,54,57],[43,46,50],[48,51,55],[50,54,57]],[62,63,66,67,69,67,66,63],melstart=1,pluckdecay=5)
