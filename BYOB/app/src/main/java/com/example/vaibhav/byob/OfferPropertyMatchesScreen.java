package com.example.vaibhav.byob;

import android.annotation.SuppressLint;
import android.content.Intent;
import android.os.Bundle;
import android.view.Gravity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.WindowManager;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.PopupWindow;
import android.widget.TextView;
import android.widget.Toast;

import com.example.vaibhav.byob.utils.TimestampToDate;
import com.example.vaibhav.byob.utils.custom.adapters.MyListAdapter;
import com.example.vaibhav.byob.utils.sqlObject.PropertyTableObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

import androidx.appcompat.app.AppCompatActivity;

public class OfferPropertyMatchesScreen extends AppCompatActivity {
    
    @SuppressLint("ClickableViewAccessibility")
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        
        setContentView(R.layout.activity_offer_property_matches_screen);
        
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        
        try {
            Objects.requireNonNull(getSupportActionBar()).hide();
        } catch (Exception ignored) {
        
        }
        
        ListView matchedProperties = findViewById(R.id.matchedProperties);
        
        Bundle extra = getIntent().getBundleExtra(getString(R.string.matches_intent_key));
        ArrayList<PropertyTableObject> propertyTableObjects = (ArrayList<PropertyTableObject>) extra.getSerializable("objects");
        
        Map<String, String> dataContainer = new HashMap<>();
        
        assert propertyTableObjects != null;
        for (PropertyTableObject propertyTableObject : propertyTableObjects) {
            
            TimestampToDate timestampToDate = new TimestampToDate();
            String date = timestampToDate.epoch2DateString(propertyTableObject.getEpochTime(), "E-dd-MMM");
            StringBuilder dateToBeDisplayed = new StringBuilder();
            String[] dateSplits = date.split("-");
            for (String dateSplit : dateSplits) {
                dateToBeDisplayed.append(dateSplit).append(System.lineSeparator());
            }
            
            dataContainer.put(dateToBeDisplayed.substring(0, dateToBeDisplayed.lastIndexOf(System.lineSeparator())),
                    propertyTableObject.getOffer_id() + "__" + propertyTableObject.getSource_address());
            
        }
        
        if (dataContainer.size() > 0) {
            
            final List<String> date = new ArrayList<>();
            final List<String> offerId = new ArrayList<>();
            final List<String> address = new ArrayList<>();
            
            for (String key : dataContainer.keySet()) {
                date.add(key);
                String[] title_subtitleContent = dataContainer.get(key).split("__");
                
                offerId.add(title_subtitleContent[0].trim());
                address.add(title_subtitleContent[1].trim());
                
            }
            
            MyListAdapter adapter = new MyListAdapter(this, date, offerId, address);
            
            matchedProperties.setAdapter(adapter);
            
            matchedProperties.setOnItemClickListener((parent, view, position, id) -> {
                
                LayoutInflater inflater = (LayoutInflater)
                        getSystemService(LAYOUT_INFLATER_SERVICE);
                View popupView = inflater.inflate(R.layout.popup_window, null);
                
                PropertyTableObject mPropertyTableObject = propertyTableObjects.get(position);
                
                TextView mSrcTextView = popupView.findViewById(R.id.property_src_detailed_popup_text_view);
                TextView mDestTextView = popupView.findViewById(R.id.property_dest_detailed_popup_text_view);
                
                String srcText = builSrcAddress(mPropertyTableObject);
                mSrcTextView.setText(srcText);
                
                String destText = buildDestAddress(mPropertyTableObject);
                mDestTextView.setText(destText);
                
                // create the popup window
                int width = LinearLayout.LayoutParams.WRAP_CONTENT;
                int height = LinearLayout.LayoutParams.WRAP_CONTENT;
                boolean focusable = true; // lets taps outside the popup also dismiss it
                final PopupWindow popupWindow = new PopupWindow(popupView, width, height, focusable);
                
                // show the popup window
                // which view you pass in doesn't matter, it is only used for the window token
                popupWindow.showAtLocation(view, Gravity.CENTER, 0, 0);
                Toast.makeText(getApplicationContext(), "Click anywhere to close pop-up", Toast.LENGTH_SHORT).show();
                
                // dismiss the popup window when touched
                popupView.setOnTouchListener((v, event) -> {
                    popupWindow.dismiss();
                    return true;
                });
            });
            
        } else {
            Toast.makeText(getApplicationContext(), "No match found.", Toast.LENGTH_SHORT).show();
            Intent intent = new Intent(getApplicationContext(), OfferPropertyActivity.class);
            startActivity(intent);
        }
        
    }
    
    public String builSrcAddress(PropertyTableObject mPropertyTableObject) {
        String content = "";
        content += mPropertyTableObject.getSource_address().replace("\\", "") + "\n";
        return content;
    }
    
    public String buildDestAddress(PropertyTableObject mPropertyTableObject) {
        String content = "";
        content += mPropertyTableObject.getDestination_address().replace("\\", "") + "\n";
        return content;
    }
    
}
