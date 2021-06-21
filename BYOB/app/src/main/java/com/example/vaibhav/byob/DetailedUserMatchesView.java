package com.example.vaibhav.byob;

import android.os.Bundle;
import android.view.WindowManager;
import android.widget.ArrayAdapter;
import android.widget.ListView;

import com.example.vaibhav.byob.utils.sqlObject.PropertyTableObject;

import java.util.ArrayList;
import java.util.Objects;

import androidx.appcompat.app.AppCompatActivity;

public class DetailedUserMatchesView extends AppCompatActivity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_detailed_user_matches_view);
        
        setContentView(R.layout.activity_offer_property_matches_screen);
        
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        
        try {
            Objects.requireNonNull(getSupportActionBar()).hide();
        } catch (Exception ignored) {
        
        }
    
        ListView matchedProperties = findViewById(R.id.matchedPropertiesDetailedView);
    
        Bundle extra = getIntent().getBundleExtra(getString(R.string.matches_intent_key));
        ArrayList<PropertyTableObject> objects = (ArrayList<PropertyTableObject>) extra.getSerializable("objects");
    
        ArrayList<String> propertySource = new ArrayList<>();
        assert objects != null;
        for (PropertyTableObject object : objects) {
            propertySource.add(object.getSource_address());
        }
    
        ArrayAdapter<String> arrayAdapter = new ArrayAdapter<>(this, android.R.layout.simple_list_item_1, propertySource);
        matchedProperties.setAdapter(arrayAdapter);
    
    }
}
