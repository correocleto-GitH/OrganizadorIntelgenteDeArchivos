data=open(r"c:\organizador_archivos\app.py",encoding="utf-8").read(); idx=data.find("Ã"); print(repr(data[idx-10:idx+20]) if idx>=0 else "not found")
