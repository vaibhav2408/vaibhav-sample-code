package com.example.vaibhav.byob;

import android.os.Bundle;
import android.view.WindowManager;

import java.util.Objects;

import androidx.appcompat.app.AppCompatActivity;

public class ShortlistedProperties extends AppCompatActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        
        try {
            Objects.requireNonNull(getSupportActionBar()).hide();
        } catch (Exception ignored) {
        
        }
        
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        
    }
    
}
