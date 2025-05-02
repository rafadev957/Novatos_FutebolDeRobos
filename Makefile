PROTOC  = protoc 
PROTO_DEP = $(wildcard pb/proto/*.proto)

all: $(PROTO_DEP)
	$(PROTOC) -Ipb/proto --python_out=pb/ $^

clean:
	rm -rf pb/*.py

