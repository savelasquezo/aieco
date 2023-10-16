#!/bin/bash

export FECHA=`date +%d_%m_%Y_%H_%M_%S`
export NAME=${FECHA}.dump
export DIR=/home/app/aieco/core/db
USER_DB=postgres
NAME_DB=dbaieco
cd $DIR
> ${NAME}
export PGPASSWORD=4oPn2655Lmn
chmod 777 ${NAME}
pg_dump -U $USER_DB -h localhost --port 5432 -f ${NAME} $NAME_DB
