#!/usr/bin/env python3
"""Offline, dependency-free release manifest validation. Never uploads or publishes."""
import argparse, json, pathlib, sys
def validate(data):
    errors=[]
    artist=data.get("artist",{})
    release=data.get("release",{})
    for label,value in [("artist.name",artist.get("name")),("release.title",release.get("title")),("release.cover_file",release.get("cover_file")),("release.rights_holder",release.get("rights_holder"))]:
        if not isinstance(value,str) or not value.strip(): errors.append("Missing "+label)
    tracks=release.get("tracks")
    if not isinstance(tracks,list) or not tracks: errors.append("No tracks provided")
    else:
        for i,t in enumerate(tracks,1):
            for key in ("title","wav_file"):
                if not isinstance(t.get(key),str) or not t[key].strip(): errors.append(f"Track {i}: missing {key}")
            if t.get("wav_file") and not pathlib.Path(t["wav_file"]).is_file(): errors.append(f"Track {i}: WAV not found: {t['wav_file']}")
    cover=release.get("cover_file")
    if cover and not pathlib.Path(cover).is_file(): errors.append("Cover file not found: "+cover)
    return errors
def main():
    p=argparse.ArgumentParser()
    p.add_argument("manifest")
    args=p.parse_args()
    data=json.loads(pathlib.Path(args.manifest).read_text(encoding="utf-8"))
    errors=validate(data)
    print(json.dumps({"ready":not errors,"errors":errors},ensure_ascii=False,indent=2))
    return 1 if errors else 0
if __name__=="__main__":sys.exit(main())
