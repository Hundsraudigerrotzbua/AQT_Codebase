//Polling Acquisition Sample
//The sample will open the first camera attached
//and acquire 5 frames using a polling scheme.

#define TIMEOUT		-1//infinite

#include <stdlib.h>
#include <fstream>
#include "Python.h"
#include "stdio.h"
#include "picam.h"
#include "picam_advanced.h"

void PrintData( pibyte* buf, pi64s numframes, piint framelength )
{
    pi16u  *midpt = NULL;
    pibyte *frameptr = NULL;

    for( piint loop = 0; loop < numframes; loop++ )
    {
        frameptr = buf + ( framelength * loop );
        midpt = (pi16u*)frameptr + ( ( ( framelength/sizeof(pi16u) )/ 2 ) );
        printf( "%5d,%5d,%5d\n", (int) *(midpt-1),(int) *(midpt), (int) *(midpt+1) );
    }
}

// argv[1] = (int) Frequency Steps in Hz
// argv[2] = (int) Averges n_avg
// argv[3] = (int) Exposure time
// argv[4] = (int) EM Gain
// argv[5] = (char) Saving Name
// argv[6] = (int) Framecount
int main(int argc, char * argv[])
{
    if(argc<6){
        fprintf(stderr, "Too few arguments to process camera call.");
        return 1;
    }
    printf("Initializing library...");
    Picam_InitializeLibrary();
    printf("PICAM initialized.");

    // - open the first camera if any or create a demo camera
	pibln bRunning;
	pibln committed;
    PicamHandle camera;
    PicamCameraID id;
    const pichar* string;
    PicamAvailableData data;
    PicamAcquisitionStatus status;
    piint readoutstride = 0;
	PicamError err;
	pi64s framecount = 0;
    piint FRAMES = atoi(argv[6]);
    //char opxScript[] = "D:\\QM_OPX\\scrapyard\\widefield_odmr.py";
    //Py_SetProgramName((wchar_t*)opxScript);
    FILE* fp;


    printf("Establishing connection to camera...");
    if( Picam_OpenFirstCamera( &camera ) == PicamError_None )
        Picam_GetCameraID( camera, &id );
    else
    {
        Picam_ConnectDemoCamera(
            PicamModel_Pixis100F,
            "0008675309",
            &id );
        Picam_OpenCamera( &id, &camera );
        printf( "No Camera Detected, Creating Demo Camera\n" );
    }
    Picam_GetEnumerationString( PicamEnumeratedType_Model, id.model, &string );
    printf( "Connected to: %s", string );
    printf( " (SN:%s) [%s]\n", id.serial_number, id.sensor_name );
    Picam_DestroyString( string );

    Picam_GetParameterIntegerValue( camera, PicamParameter_ReadoutStride, &readoutstride );
    Picam_SetParameterLargeIntegerValue( camera, PicamParameter_ReadoutCount, FRAMES);
    Picam_SetParameterIntegerValue( camera, PicamParameter_TriggerResponse, PicamTriggerResponse_ReadoutPerTrigger );
	Picam_SetParameterIntegerValue( camera, PicamParameter_TriggerDetermination, PicamTriggerDetermination_RisingEdge);
    Picam_SetParameterFloatingPointValue( camera, PicamParameter_ExposureTime, atof(argv[3]));
    Picam_SetParameterIntegerValue( camera, PicamParameter_AdcEMGain, atoi(argv[4]));

	Picam_AreParametersCommitted( camera, &committed );
	if( !committed )
	{
		const PicamParameter* failed_parameter_array = NULL;
		piint           failed_parameter_count = 0;
		Picam_CommitParameters( camera, &failed_parameter_array, &failed_parameter_count );
		if( failed_parameter_count )
		{
		    Picam_DestroyParameters( failed_parameter_array );
		}
	}
    printf( "Collecting %i frames\n", FRAMES);
	err = Picam_StartAcquisition( camera );
	bRunning = ( err == PicamError_None );
    std::ofstream ofs;
    ofs.open(argv[5], std::ios::out | std::ios::binary);
    //printf( "Ready to receive Triggers\nStarting OPX from %s...\n", opxScript);

    //Py_Initialize();
    //fp = _Py_fopen(opxScript, "r");
    //PySys_SetArgv(argc, (wchar_t**)argv);
        
    //if (!PyRun_SimpleFile(fp, opxScript)){
    //    printf( "OPX started successfully.");
    //} else {
    //    printf( "Error in OPX setup.");
    //    Py_Finalize();
    //    Picam_StopAcquisition( camera );
    //    ofs.close();
    //    return 1;
    //}
    //Py_Finalize();

	while( bRunning )
	{
		err = Picam_WaitForAcquisitionUpdate( camera, TIMEOUT, &data, &status );
		if( err == PicamError_None )
		{
			bRunning = status.running;
            ofs.write(reinterpret_cast<pichar*>(data.initial_readout), (readoutstride));
            framecount += data.readout_count;
            printf("Frame Nr. %i\n", framecount);
		}
		else if( err == PicamError_TimeOutOccurred )
		{
			printf( "Terminating prematurely!  Try increasing time out\n" );
			Picam_StopAcquisition( camera );
            ofs.close();
		}
	}
    ofs.close();
    Picam_CloseCamera( camera );
    Picam_UninitializeLibrary();
}
