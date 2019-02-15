using System;

using AppKit;
using CoreFoundation;
using Foundation;

namespace MessageSender
{
	public partial class MainWindowController : NSWindowController, INSTextFieldDelegate
	{
		CFMessagePort msgPort;

        CFMessagePort localPort;

        public new MainWindow Window {
			get {
				return (MainWindow)base.Window;
			}
		}

		public MainWindowController (IntPtr handle) : base (handle)
		{
		}

		[Export ("initWithCoder:")]
		public MainWindowController (NSCoder coder) : base (coder)
		{
		}

		public MainWindowController () : base ("MainWindow")
		{
		}

		public override void AwakeFromNib ()
		{
            localPort = CFMessagePort.CreateLocalPort("com.example.app.port.xamarin.server", (int type, NSData data)=> {
                //Console.WriteLine("Data = {0}", data);

                var alert = new NSAlert
                {
                    MessageText = "Data = " + data
                };
                alert.AddButton("OK");
                alert.RunSheetModal(Window);

                return new NSData();
            } );

            var runLoopSource = localPort.CreateRunLoopSource();
            CFRunLoop.Current.AddSource(runLoopSource, CFRunLoop.ModeCommon);

			TheButton.Activated += SendMessage;
			TextField.WeakDelegate = this;
        }

        void HandleCFMessagePortCallBack(int type, NSData data)
        {
        }


        [Export("controlTextDidEndEditing:")]
		public void EditingEnded(NSNotification notification)
		{
			var textMovement = notification.UserInfo.ObjectForKey ((NSString)"NSTextMovement");
			var interactionCode = ((NSNumber)textMovement).Int32Value;
			var textMovementType = (NSTextMovement)interactionCode;
			if (textMovementType == NSTextMovement.Return)
				SendMessage (null,null);
		}

		void SendMessage (object sender, EventArgs e)
		{
			using (var data = NSData.FromString (TextField.StringValue)) {

                msgPort = CFMessagePort.CreateRemotePort(CFAllocator.Default, "com.example.app.port.server");
                if (msgPort == null)
                {
                    var alert = new NSAlert
                    {
                        MessageText = "Unable to connect to port? Did you launch server first?"
                    };
                    alert.AddButton("OK");
                    alert.RunSheetModal(Window);
                }

                NSData responseData;
                CFMessagePortSendRequestStatus status = msgPort.SendRequest (0x111, data, 10.0, 10.0, (NSString)string.Empty, out responseData);
				//TextField.StringValue = string.Empty;
            }
		}
	}
}
