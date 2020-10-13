/* 
 * File:   Dispev.cpp
 * Author: mbustreo
 *
 * Created on 07 July 2015
 *
 * Implementation of the algorithm described in "A two-stage correlation method for stereoscopic depth estimation" 
 * by Nils Einecke, and Julian Eggert [DICTA, page 227-234. IEEE Computer Society, (2010)]
 *
 * Note that algorithm can be strongly speeded-up.
 *
 */

#include <opencv2/core/core.hpp>
#include <opencv2/highgui/highgui.hpp>
#include <opencv2/imgproc/imgproc.hpp>
#include <iostream>
#include <fstream>
#include<string>

#include "utilities.h"

using namespace cv;
using namespace std;

struct Inputs
{
	string imgNameL;
	string imgNameR;
	 
	int maxDisp;
	int minDisp;

	int boxFilterSizeX;
	int boxFilterSizeY;
	int sumFilterSizeX;
	int sumFilterSizeY;
};

void help()
{
	cout << "Usage Example: Dispev.exe C:\\leftPic.jpg C:\\rightPic.jpg  maxDisp minDisp boxFilterSizeX boxFilterSizeY sumFilterSizeX sumFilterSizeX" << endl;
	
	cout << " - maxDisp and minDisp represent the disparity interval the algorithm will search for correspondence." << endl;
	cout << "   -- DEFAULT VALUES: If not inserted maxDisp and minDisp are set to 60 and 1;" << endl;
	
	cout << " - (boxFilterSizeX, boxFilterSizeY) represent the correlation filter size." << endl;
	cout << "   -- DEFAULT VALUES: If not inserted (boxFilterSizeX, boxFilterSizeY) is set to (3,3);" << endl;
	
	cout << " - (sumFilterSizeX, sumFilterSizeY) represent the summation filter size." << endl;
	cout << "   -- DEFAULT VALUES: If not inserted (sumFilterSizeX, sumFilterSizeY) is set to (5,9);" << endl;
}

int readArgs ( int argc, char** argv, Inputs &in )
{
	cout << "Reading inputs...." << endl << endl;
	
	if( argc < 3)	
	{
		help();
		return -1;
	}

	in.maxDisp = 60;		
	in.minDisp = 1;	

	in.boxFilterSizeX = 3;
	in.boxFilterSizeY = 3;
	in.sumFilterSizeX = 5;
	in.sumFilterSizeY = 9;

	switch (argc)
	{
		default:
		case 8:
			in.sumFilterSizeY = atoi(argv[7]);
		case 7:
			in.sumFilterSizeX = atoi(argv[6]);
		case 6:
			in.boxFilterSizeY = atoi(argv[5]);	
		case 5:
			in.boxFilterSizeX = atoi(argv[4]);	
		case 4:
			in.minDisp = atoi(argv[3]);	
		case 3:
			in.maxDisp = atoi(argv[2]);	
		case 2:
			char imgNameL[100];
			char imgNameR[100];
			sprintf(imgNameL, "InputImages/FullSize/training/%s/im0.png",  argv[1]);
			sprintf(imgNameR, "InputImages/FullSize/training/%s/im1.png", argv[1]);
			in.imgNameL = imgNameL;
			in.imgNameR = imgNameR;
			break;
	}

	// -- CHECKING INPUTS VALIDITY
	
	// Verifying if disparity threashold are reasonable
    if(in.minDisp >= in.maxDisp ) 
	{
        cout << "minDisp should be less than maxDisp!" << std::endl ;
        return -1;
    }
	
	// Verifying correlation window sizes are odd, otherwise increment by 1
	if(in.boxFilterSizeX%2==0) 
	{
        cout << "Correlation window X size dimensions should be odd! Automatically increased of 1." << std::endl ;
        in.boxFilterSizeX++;
    }
	
	if(in.boxFilterSizeY%2==0) 
	{
        cout << "Correlation window Y size dimensions should be odd! Automatically increased of 1." << std::endl ;
        in.boxFilterSizeY++;
    }

	// Verifying summation window sizes are odd, otherwise increment by 1
	if(in.sumFilterSizeX%2==0) 
	{
        cout << "Correlation window X size dimensions should be odd! Automatically increased of 1." << std::endl ;
        in.sumFilterSizeX++;
    }
	
	if(in.sumFilterSizeY%2==0) 
	{
        cout << "Correlation window Y size dimensions should be odd! Automatically increased of 1." << std::endl ;
        in.sumFilterSizeY++;
    }
	
	cout << " - maxDisp set to... " << in.maxDisp << endl;
	cout << " - minDisp set to... " << in.minDisp << endl;
	cout << " - (boxFilterSizeX, boxFilterSizeY) set to... (" << in.boxFilterSizeX << ", " << in.boxFilterSizeY << ")" << endl;
	cout << " - (sumFilterSizeX, sumFilterSizeY) set to... (" << in.sumFilterSizeX << ", " << in.sumFilterSizeY << ")" << endl;
	cout << endl;

	return 0;
}

void translateImg(const Mat &img, Mat &outImg, int offsetx, int offsety)
{
	Mat trans_mat = (Mat_<double>(2,3) << 1, 0, offsetx, 0, 1, offsety);
	warpAffine(img, outImg, trans_mat, img.size());
}

int main( int argc, char** argv )
{
	// Reading inputs arguments
	Inputs in;
	int retVal = readArgs(argc, argv, in);

	if( retVal < 0 )	return retVal;

	setUseOptimized(true);

	// Loading images
    Mat imgL, imgR;
    imgL = imread(in.imgNameL, IMREAD_GRAYSCALE ); 
	imgR = imread(in.imgNameR, IMREAD_GRAYSCALE );

	// Verifying if images has been correctly loaded
    if(! imgL.data ) 
    {
        cout << "Left image impossible to read" << std::endl ;
        return -1;
    }

	if(! imgR.data ) 
    {
        cout << "Right image impossible to read" << std::endl ;
        return -1;
    }

	// Verifying images are of the same size
	if(imgR.rows != imgL.rows || imgR.cols != imgL.cols) 
    {
        cout << "Size of images have to be equal!" << std::endl ;
        return -1;
    }

	// Visualizing input images
	/*
	namedWindow( "Left Image", WINDOW_NORMAL); 
	cv::resizeWindow("Left Image", 640, 480);
    imshow( "Left Image", imgL ); 

	namedWindow( "Right Image", WINDOW_NORMAL); 
	cv::resizeWindow("Right Image", 640, 480);
    imshow( "Right Image", imgR ); 
	*/
	
	// --> 
	
	
	// Converting input images to double precision
	Mat imgL64, imgR64;
	imgL.convertTo(imgL64, CV_64F);
	imgR.convertTo(imgR64, CV_64F);

	// ** SNCC INIT **
	Mat meanL, meanR, meanLL, meanRR;
	Mat sigmaL, sigmaR;

	// Calculating meanL and meanR using separable filters
	boxFilter(imgL64, meanL, CV_64F, Size(in.boxFilterSizeX, in.boxFilterSizeY));		// #SNCC Init (1)
	boxFilter(imgR64, meanR, CV_64F, Size(in.boxFilterSizeX, in.boxFilterSizeY));		// #SNCC Init (2)

	// Calculating sigmaL and sigmaR using separable filters
	boxFilter(imgL64.mul(imgL64), meanLL, CV_64F, Size(in.boxFilterSizeX, in.boxFilterSizeY));				
	boxFilter(imgR64.mul(imgR64), meanRR, CV_64F, Size(in.boxFilterSizeX, in.boxFilterSizeY));				

	sqrt((meanLL - meanL.mul(meanL)), sigmaL);			// #SNCC Init (3)
	sqrt((meanRR - meanR.mul(meanR)), sigmaR);			// #SNCC Init (4)
	

	// Initializing disparity map and matrix containing best correlation values
	Mat_<int> dispMap(imgL.rows, imgL.cols, CV_16U);
	dispMap = 0;

	Mat bestCorrVals(imgL.rows, imgL.cols, CV_64F);
	bestCorrVals = -std::numeric_limits<double>::max();

	// Evaluating elapsed time
	double t = (double)getTickCount(); 
	
	sigmaL.setTo(1e-10, sigmaL==0);
	
	// ** SNCC LOOP ** 
	for(int d=in.minDisp; d<in.maxDisp; d++)
	{
		if(d%10==0)	cout << "Evaluating disparity value " << d << "..." << endl;

		if(d==0)	continue;

		// generating the translated version of imgR, meanR and sigmaR
		Mat imgR64d, meanRd, sigmaRd, goodValsMaskd;
		Mat corrVal (imgL.rows, imgL.cols, CV_64F);

		translateImg(imgR64, imgR64d, d, 0);
		translateImg(meanR,  meanRd,  d, 0);
		translateImg(sigmaR, sigmaRd, d, 0);
		
		sigmaRd.setTo(1e-10, sigmaRd==0);

		// #SNCC Loop (1.1)
		Mat boxFiltLRd;
		boxFilter(imgL64.mul(imgR64d), boxFiltLRd, CV_64F, Size(in.boxFilterSizeX, in.boxFilterSizeY));
		corrVal = (boxFiltLRd - meanL.mul(meanRd))/(sigmaL.mul(sigmaRd));
		
		// #SNCC Loop (1.2)
		Mat meanCorrVal ;
		boxFilter(corrVal, meanCorrVal, CV_64F, Size(in.sumFilterSizeX, in.sumFilterSizeY));	
		
		// Looking for pixels where meanCorrVal is bigger than bestCorrVals
		Mat biggerMask(imgL.rows, imgL.cols, CV_64F);
		biggerMask = meanCorrVal > bestCorrVals;
		
		char fileNameTest[1000];
		
		// Updating disparity map and matrix containing best correlation values
		dispMap.setTo(d, biggerMask);
		meanCorrVal.copyTo(bestCorrVals, biggerMask);
	}

	// Evaluating elapsed time
	t = ((double)getTickCount() - t)/getTickFrequency(); 
	cout << "Times passed in seconds: " << t << std::endl;

	// Saving results
	char fileName[1000];
	
	double min, max;
	cv::minMaxLoc(dispMap, &min, &max);
	
	cout << min << " " << max << endl;

	//Writing to file able to read 16 bit
	sprintf(fileName, "OutputImages/FullSize/training/%s/sncc_filter_%d_%d_sum_%d_%d_disp_map.yml", argv[1],in.boxFilterSizeX, in.boxFilterSizeY, in.sumFilterSizeX, in.sumFilterSizeY);
	cv::FileStorage storage(fileName, cv::FileStorage::WRITE);
	storage << "dispMap" << dispMap;
	storage.release();  
	
	
	return 0;
}