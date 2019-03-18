SHUTTLEDIR=/Users/jokedurnez/Documents/openlattice/shuttle/
INTEGRATIONSDIR=/Users/jokedurnez/Documents/Integrations/CAFE-integrations/
CODEDIR=/Users/jokedurnez/Documents/accounts/CAFE/CAFE_code/
shuttle=$SHUTTLEDIR/shuttle-0.0.4-SNAPSHOT/bin/shuttle

participant_decoding_file="/Users/jokedurnez/Box/CAFE Consortium/ParticipantIDs/participant_master/Participants_2019-03-15.csv"

cd $CODEDIR/integration

jwt = "*"
# python -i create_org_and_roles.py

##################
# TIME USE DIARY #
##################

tud_file="/Users/jokedurnez/Box/CAFE Consortium/ParticipantIDs/processed_datasets/TUD_v3_Combined.csv"
tud_file_cleaned="/Users/jokedurnez/Box/CAFE Consortium/ParticipantIDs/processed_datasets/TUD_v3_Combined_Cleaned.csv"
presurvey_file="/Users/jokedurnez/Box/CAFE Consortium/ParticipantIDs/processed_datasets/Presurveys_Combined.csv"

Rscript preintegration_tud.R "$tud_file" "$tud_file_cleaned" "$participant_decoding_file" "$presurvey_file"
echo "WIAMP"
python -i integrate_tud.py --cleanfile "$tud_file_cleaned" --study=WIAMP --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt
echo "GU"
python -u integrate_tud.py --cleanfile "$tud_file_cleaned" --study=GU --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 
echo "UWCRT"
python -u integrate_tud.py --cleanfile "$tud_file_cleaned" --study=UWCRT --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 
echo "UM"
python -u integrate_tud.py --cleanfile "$tud_file_cleaned" --study=UM --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 
echo "PM"
python -u integrate_tud.py --cleanfile "$tud_file_cleaned" --study=PM --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 

#######
# MAQ #
#######

echo "WIAMP"
rawfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/MAQS for WI Studies - as of Feb 6 2019/CAFE+Questionnaire+v.2+-+Physio+Study+(WI-AMP-BTV)_February+6,+2019_09.01 - CHOICE TEXT.csv"
cleanfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/MAQS for WI Studies - as of Feb 6 2019/CAFE+Questionnaire+v.2+-+Physio+Study+(WI-AMP-BTV)_February+6,+2019_09.01 - CHOICE TEXT_cleanIDS.csv"
id_column='Q262'

Rscript preintegration_maq.r "$rawfile" "$cleanfile" "$participant_decoding_file" "$id_column"
python -u integrate_MAQ.py --cleanfile "$cleanfile" --study=WIAMP --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 

echo "UM"
rawfile="/Users/jokedurnez/Box/UM Open Lattice Data/UM MAQS/DS_PTS_MAQS_V3.1_021519.csv"
demographyfile="/Users/jokedurnez/Box/UM Open Lattice Data/UM MAQS/DS_PTS_RedcapDemog_021519.csv"
cleanfile="/Users/jokedurnez/Box/UM Open Lattice Data/UM MAQS/DS_PTS_MAQS_V3.1_021519_cleanIDs.csv"
id_column='Q281'

Rscript preintegration_maq.r "$rawfile" "$cleanfile" "$participant_decoding_file" "$id_column" "$demographyfile"
python -u integrate_MAQ.py --cleanfile "$cleanfile" --study=UM --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 

echo "BYU"
rawfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/BYU/MAQs_BYU_V3_2018_20181004_Returning.xlsx"
cleanfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/BYU/MAQs_BYU_V3_2018_20181004_Returning_cleanIDs.csv"
id_column="Q281"

Rscript preintegration_maq.r "$rawfile" "$cleanfile" "$participant_decoding_file" "$id_column" 
python -u integrate_MAQ.py --cleanfile "$cleanfile" --study=BYU --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 

echo "GU"
rawfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/GU/GU_MAQs_11March2019_ChoiceText.csv"
rawfile2="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/GU/GU_MAQs_11March2019_SecondFile_ChoiceText.csv"
cleanfile="/Users/jokedurnez/Box/CAFE Consortium/Open Lattice Dashboard and Data Integration/GU/GU_MAQs_11March2019_ChoiceText_cleanIDs.csv"
id_column="Q281"

Rscript preintegration_maq.r "$rawfile" "$cleanfile" "$participant_decoding_file" "$id_column" "" "$rawfile2"
python -u integrate_MAQ.py --cleanfile "$cleanfile" --study=GU --codedir=$CODEDIR --integrationsdir=$INTEGRATIONSDIR --shuttle=$shuttle --jwt=$jwt 
