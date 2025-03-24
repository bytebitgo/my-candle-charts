package com.mt5candlechart.tv;

import android.os.Bundle;
import android.view.KeyEvent;
import android.view.View;
import android.webkit.WebView;

import com.getcapacitor.BridgeActivity;

public class MainActivity extends BridgeActivity {
    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        // 设置全屏显示
        View decorView = getWindow().getDecorView();
        decorView.setSystemUiVisibility(
            View.SYSTEM_UI_FLAG_LAYOUT_STABLE
            | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
            | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
            | View.SYSTEM_UI_FLAG_FULLSCREEN
            | View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY);
            
        // 配置WebView
        WebView webView = getBridge().getWebView();
        webView.setFocusable(true);
        webView.setFocusableInTouchMode(true);
        webView.requestFocus();
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        WebView webView = getBridge().getWebView();
        
        // 处理D-pad按键事件
        if (event.getAction() == KeyEvent.ACTION_DOWN) {
            switch (event.getKeyCode()) {
                case KeyEvent.KEYCODE_DPAD_UP:
                    webView.evaluateJavascript("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowUp'}))", null);
                    return true;
                case KeyEvent.KEYCODE_DPAD_DOWN:
                    webView.evaluateJavascript("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowDown'}))", null);
                    return true;
                case KeyEvent.KEYCODE_DPAD_LEFT:
                    webView.evaluateJavascript("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowLeft'}))", null);
                    return true;
                case KeyEvent.KEYCODE_DPAD_RIGHT:
                    webView.evaluateJavascript("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'ArrowRight'}))", null);
                    return true;
                case KeyEvent.KEYCODE_DPAD_CENTER:
                case KeyEvent.KEYCODE_ENTER:
                    webView.evaluateJavascript("window.dispatchEvent(new KeyboardEvent('keydown', {key: 'Enter'}))", null);
                    return true;
            }
        }
        return super.dispatchKeyEvent(event);
    }
}
