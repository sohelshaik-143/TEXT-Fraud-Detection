package com.fraudguard.app;

import com.getcapacitor.JSObject;
import com.getcapacitor.Plugin;
import com.getcapacitor.annotation.CapacitorPlugin;

@CapacitorPlugin(name = "SMSPlugin")
public class SMSPlugin extends Plugin {

    public void onSMSReceived(String sender, String message) {
        JSObject ret = new JSObject();
        ret.put("sender", sender);
        ret.put("message", message);
        notifyListeners("smsReceived", ret);
    }
}
