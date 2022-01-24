all: rpm

rpm:
	mkdir -p BUILD
	mkdir -p BUILDROOT
	mkdir -p SOURCES
	mkdir -p SPECS
	mkdir -p RPMS
	mkdir -p SRPMS

	cp -r dist BUILD/
	cp -r conf BUILD/
	cp megatron-gui.spec SPECS/
	rpmbuild --define "_topdir `pwd`" -bb SPECS/megatron-gui.spec
	cp RPMS/noarch/* .

clean:
	rm -rf BUILD
	rm -rf BUILDROOT
	rm -rf SOURCES
	rm -rf SPECS
	rm -rf RPMS
	rm -rf SRPMS
	rm -f *.rpm
