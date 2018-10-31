#!/bin/bash

INSTALLDIR=/opt/bucephalus

rm -r $INSTALLDIR
mkdir $INSTALLDIR
cp app/dbops.py $INSTALLDIR
cp app/bucadd.py $INSTALLDIR
cp app/server.py $INSTALLDIR
cp app/bucrm.py $INSTALLDIR
cp app/config.py $INSTALLDIR
cp app/search.py $INSTALLDIR
cp app/bucvac.py $INSTALLDIR
cp app/bucfup.py $INSTALLDIR
cp app/tasklist.py $INSTALLDIR
cp -R app/static $INSTALLDIR
cp -R app/templates $INSTALLDIR
cp -R app/prototypes $INSTALLDIR

printf "#!/bin/bash\n FLASK_APP=\"$INSTALLDIR/server.py\" flask run \"\$@\"\n" > /usr/local/bin/bucserve
printf "#!/bin/bash\n exec python $INSTALLDIR/bucadd.py \"\$@\" \n" > /usr/local/bin/bucadd
printf "#!/bin/bash\n exec python $INSTALLDIR/bucvac.py \"\$@\" \n" > /usr/local/bin/bucvac
printf "#!/bin/bash\n exec python $INSTALLDIR/bucfup.py \"\$@\" \n" > /usr/local/bin/bucfup
printf "#!/bin/bash\n exec python $INSTALLDIR/bucrm.py \"\$@\" \n" > /usr/local/bin/bucrm
chmod a+rx /usr/local/bin/bucserve
chmod a+rx /usr/local/bin/bucadd
chmod a+rx /usr/local/bin/bucfup
chmod a+rx /usr/local/bin/bucvac
chmod a+rx /usr/local/bin/bucrm
