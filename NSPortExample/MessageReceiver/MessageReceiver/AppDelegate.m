//
//  AppDelegate.m
//  MessageReciever
//
//  Created by Chris Hamons on 6/4/15.
//  Copyright (c) 2015 Chris Hamons. All rights reserved.
//

#import "AppDelegate.h"

@interface AppDelegate ()

@property (weak) IBOutlet NSWindow *window;
@end

static CFDataRef Callback(CFMessagePortRef port,
                          SInt32 messageID,
                          CFDataRef data,
                          void *info)
{
    
    NSString* newStr = [NSString stringWithUTF8String:[(__bridge NSData*)data bytes]];
    [(AppDelegate*)[NSApp delegate] addItem:newStr];
    return nil;
}


@implementation AppDelegate
- (IBAction)SendMessage:(id)sender {
    //self.messageText.stringValue = @"Send Message.";
    
    CFMessagePortRef remotePort = CFMessagePortCreateRemote(kCFAllocatorDefault, CFSTR("com.example.app.port.xamarin.server"));
    
    if(nil == remotePort)
    {
        NSAlert *alert = [[NSAlert alloc] init];
        [alert setMessageText:@"portエラー"];
    }
    else
    {
        NSString    *msg = [NSString stringWithFormat:@"%@",self.messageText.stringValue];
        NSLog(@"send msg is :%@",msg);
        const char *message = [msg UTF8String];
        CFDataRef data,recvData = nil;
        data = CFDataCreate(NULL, (UInt8 *)message, strlen(message));
        
        CFMessagePortSendRequest(remotePort, 0x11, data, 0, 100 , kCFRunLoopDefaultMode, &recvData);

        CFRelease(data);
        CFMessagePortInvalidate(remotePort);
        CFRelease(remotePort);
        
    }
}

// Based on http://nshipster.com/inter-process-communication/
- (void)applicationDidFinishLaunching:(NSNotification *)aNotification {
    // Quick hack to show messages recieved
    self.TheTable.delegate = self;
    self.TheTable.dataSource = self;
    self.TheTable.headerView = nil;
    
    values = [NSMutableArray new];
    
    CFMessagePortRef localPort = CFMessagePortCreateLocal(nil, CFSTR("com.example.app.port.server"), Callback, nil, nil);
    CFRunLoopSourceRef runLoopSource = CFMessagePortCreateRunLoopSource(nil, localPort, 0);
    CFRunLoopAddSource(CFRunLoopGetCurrent(), runLoopSource, kCFRunLoopCommonModes);
    
}

- (void)applicationWillTerminate:(NSNotification *)aNotification {
    // Insert code here to tear down your application
}

NSMutableArray * values;

- (void) addItem:(NSString *)string {
    [values addObject:string];
    [self.TheTable reloadData];
    [self.TheTable sizeToFit];
}

- (NSInteger)numberOfRowsInTableView:(NSTableView *)tableView {
    return values.count;
}

- (NSView *)tableView:(NSTableView *)tableView viewForTableColumn:(NSTableColumn *)tableColumn row:(NSInteger   )row {
    NSTextField * view = [tableView makeViewWithIdentifier:@"MyCustomView" owner:self];
    if (view == nil) {
        view = [NSTextField new];
        view.identifier = @"MyCustomView";
        view.bordered = false;
        view.selectable = false;
        view.editable = false;
    }
    view.stringValue = [values objectAtIndex:row];
    return view;
}

@end
