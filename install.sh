#!/bin/bash

INSTALLDIR=/opt/bucephalus

mkdir $INSTALLDIR
cp app/dbops.py $INSTALLDIR
cp app/bucadd.py $INSTALLDIR
cp app/server.py $INSTALLDIR
cp -R app/static $INSTALLDIR
cp -R app/templates $INSTALLDIR
cp -R horsepee/prototypes $INSTALLDIR
cp horsepee/horsepee.py $INSTALLDIR
cp horsepee/build.sh $INSTALLDIR/texbuilder.sh

printf "#!/bin/bash\n FLASK_APP=\"$INSTALLDIR/server.py\" flask run \$@\n" > /usr/local/bin/bucserve
printf "#!/bin/bash\n exec python $INSTALLDIR/bucadd.py \$@\n" > /usr/local/bin/bucadd
printf "#!/bin/bash\n exec bash $INSTALLDIR/texbuilder.sh \$@\n" > /usr/local/bin/buctex
chmod a+rx /usr/local/bin/bucserve
chmod a+rx /usr/local/bin/bucadd
chmod a+rx /usr/local/bin/buctex
