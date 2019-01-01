#!/bin/bash

INSTALLDIR=/opt/bucephalus

rm -r $INSTALLDIR
mkdir $INSTALLDIR
cp -R bin $INSTALLDIR
cp -R web $INSTALLDIR
cp -R lib $INSTALLDIR
cp -R prototypes $INSTALLDIR
cp -R stencils $INSTALLDIR

printf "#!/bin/bash\n FLASK_APP=\"$INSTALLDIR/web/server.py\" PYTHONPATH=\"$PYTHONPATH:$INSTALLDIR/lib\" flask run \"\$@\"\n" > /usr/local/bin/bucserve
chmod a+rx /usr/local/bin/bucserve

function wrapperscript {
  PLACE="/usr/local/bin/$1"
  echo "#!/bin/bash" > $PLACE
  echo "export PYTHONPATH=\"$PYTHONPATH:$INSTALLDIR/lib\"" >> $PLACE
  echo "exec python3 $INSTALLDIR/bin/$1.py \"\$@\"" >> $PLACE
  chmod a+rx $PLACE
}

wrapperscript bucadd
wrapperscript bucvac
wrapperscript bucfup
wrapperscript bucmup
wrapperscript bucrm
wrapperscript buctask
wrapperscript bucdef
wrapperscript buchp2
