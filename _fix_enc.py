import sys; data=open(sys.argv[1],encoding="utf-8").read(); fixed=data.encode("latin-1").decode("utf-8"); open(sys.argv[1],"w",encoding="utf-8").write(fixed); print("done")
