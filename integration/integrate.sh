SHUTTLEDIR=/Users/jokedurnez/Documents/openlattice/shuttle/
INTEGRATIONSDIR=/Users/jokedurnez/Documents/Integrations/CAFE-integrations/
CODEDIR=/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/

export shuttle=$SHUTTLEDIR/shuttle-0.0.4-SNAPSHOT/bin/shuttle

export cleanfile="/Users/jokedurnez/Box/CAFE Consortium/ParticipantIDs/processed_datasets/TUD_v3_Combined_Cleaned.csv"

cd $CODEDIR/integration

##################
# TIME USE DIARY #
##################

Rscript preintegration_tud.R
echo "WIAMP"
python -u integrate_tud.py --cleanfile "$cleanfile" --study=WIAMP --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
echo "BYU"+
python -u integrate_tud.py --cleanfile "$cleanfile" --study=BYU --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
echo "GU"
python -u integrate_tud.py --cleanfile "$cleanfile" --study=GU --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
echo "UWCRT"
python -u integrate_tud.py --cleanfile "$cleanfile" --study=UWCRT --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
# echo "NIRS"
python -u integrate_tud.py --cleanfile "$cleanfile" --study=NIRS --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
echo "UM"
python -u integrate_tud.py --cleanfile "$cleanfile" --study=UM --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
echo "PM"
python -u integrate_tud.py --cleanfile "$cleanfile" --study=PM --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle

#######
# MAQ #
#######

export rawfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/MAQS for WI Studies - as of Feb 6 2019/CAFE+Questionnaire+v.2+-+Physio+Study+(WI-AMP-BTV)_February+6,+2019_09.01 - CHOICE TEXT.csv"
export cleanfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/MAQS for WI Studies - as of Feb 6 2019/CAFE+Questionnaire+v.2+-+Physio+Study+(WI-AMP-BTV)_February+6,+2019_09.01 - CHOICE TEXT_cleanIDS.csv"

Rscript preintegration_maq.r "$rawfile" "$cleanfile"
echo "WIAMP"
python -i integrate_MAQ.py --cleanfile "$cleanfile" --study=WIAMP --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle
