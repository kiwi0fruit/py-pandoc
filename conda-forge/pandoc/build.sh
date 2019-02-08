#!/bin/bash

if [ $(uname) == Linux ]; then
    # conda-build tries to be smarted than you an unpackas debs now :-/
    # ar vx pandoc.deb
    tar --extract --xz --verbose --file=data.tar.xz
    mkdir -p $PREFIX/bin
    mv usr/bin/* $PREFIX/bin
fi


if [ $(uname) == Darwin ]; then
    pkgutil --expand pandoc.pkg pandoc
    cpio -i -I pandoc/pandoc.pkg/Payload
    mkdir -p $PREFIX/bin
    cp usr/local/bin/* $PREFIX/bin/
fi
