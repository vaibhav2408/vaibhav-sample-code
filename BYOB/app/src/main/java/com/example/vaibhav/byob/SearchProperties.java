package com.example.vaibhav.byob;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.ImageButton;
import android.widget.Toast;

import com.example.vaibhav.byob.utils.GetDistanceBetweenPoints;
import com.example.vaibhav.byob.utils.SharedResources;
import com.example.vaibhav.byob.utils.execution.variables.ExecutionVariables;
import com.example.vaibhav.byob.utils.sql.manager.SQLiteManager;
import com.example.vaibhav.byob.utils.sqlObject.PropertyTableObject;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.libraries.places.api.Places;
import com.google.android.libraries.places.api.model.Place;
import com.google.android.libraries.places.widget.Autocomplete;
import com.google.android.libraries.places.widget.AutocompleteActivity;
import com.google.android.libraries.places.widget.model.AutocompleteActivityMode;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

import androidx.annotation.Nullable;

public class SearchProperties extends BaseActivity {
    
    private static final int AUTOCOMPLETE_REQUEST_CODE = 22;
    private EditText mEditText;
    private static final String TAG = SearchProperties.class.getSimpleName();
    private LatLng srcLatLng;
    private boolean apartment_selected = false;
    private boolean house_villa_selected = false;
    private boolean studio_apartment_selected = false;
    private boolean farm_house_selected = false;
    private boolean serviced_apartment_selected = false;
    
    @Override
    int getContentViewId() {
        return R.layout.activity_search_properties;
    }
    
    @Override
    int getNavigationMenuItemId() {
        return R.id.property_search;
    }
    
    @Override
    void loadElements() {
        Places.initialize(getApplicationContext(), getString(R.string.google_maps_API_Key));
        
        String apiKey = getString(R.string.google_maps_API_Key);
        if (!Places.isInitialized()) {
            Places.initialize(getApplicationContext(), apiKey);
        }
    }
    
    public void onSearchCalled(View view) {
        // Set the fields to specify which types of place data to return.
        List<Place.Field> fields = Arrays.asList(Place.Field.ID, Place.Field.NAME, Place.Field.ADDRESS, Place.Field.LAT_LNG);
        // Start the autocomplete intent.
        Intent intent = new Autocomplete.IntentBuilder(
                AutocompleteActivityMode.OVERLAY, fields).setCountry("IN") //INDIA
                .build(this);
        mEditText = findViewById(view.getId());
        startActivityForResult(intent, AUTOCOMPLETE_REQUEST_CODE);
    }
    
    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == AUTOCOMPLETE_REQUEST_CODE) {
            if (resultCode == RESULT_OK) {
                Place place = Autocomplete.getPlaceFromIntent(data);
                Log.i(TAG, "Place: " + place.getName() + ", " + place.getId() + ", " + place.getAddress());
                
                String address = place.getAddress();
                LatLng latLng = place.getLatLng();
                mEditText.setText(address);
                srcLatLng = latLng;
                
            } else if (resultCode == AutocompleteActivity.RESULT_ERROR) {
                Status status = Autocomplete.getStatusFromIntent(data);
                Log.i(TAG, status.getStatusMessage());
            } else if (resultCode == RESULT_CANCELED) {
                // The user canceled the operation.
                Toast.makeText(getApplicationContext(), "Search cancelled.", Toast.LENGTH_SHORT).show();
            }
        }
    }
    
    public void update_property_icon(View view) {
        ImageButton apartment_icon;
        switch (view.getId()) {
            case R.id.apartment_icon:
                if (!apartment_selected) {
                    apartment_selected = true;
                    apartment_icon = findViewById(R.id.apartment_icon);
                    apartment_icon.setImageResource(R.drawable.apartment_colorful);
                } else {
                    apartment_selected = false;
                    apartment_icon = findViewById(R.id.apartment_icon);
                    apartment_icon.setImageResource(R.drawable.apartment_black_and_white);
                }
                break;
            case R.id.house_villa_icon:
                if (!house_villa_selected) {
                    house_villa_selected = true;
                    apartment_icon = findViewById(R.id.house_villa_icon);
                    apartment_icon.setImageResource(R.drawable.house_villa_colorful);
                } else {
                    house_villa_selected = false;
                    apartment_icon = findViewById(R.id.house_villa_icon);
                    apartment_icon.setImageResource(R.drawable.house_villa_black_and_white);
                }
                break;
            case R.id.studio_apartment_icon:
                if (!studio_apartment_selected) {
                    studio_apartment_selected = true;
                    apartment_icon = findViewById(R.id.studio_apartment_icon);
                    apartment_icon.setImageResource(R.drawable.studio_apartment_colorful);
                } else {
                    studio_apartment_selected = false;
                    apartment_icon = findViewById(R.id.studio_apartment_icon);
                    apartment_icon.setImageResource(R.drawable.studio_apartment_black_and_white);
                }
                break;
            case R.id.farm_house_icon:
                if (!farm_house_selected) {
                    farm_house_selected = true;
                    apartment_icon = findViewById(R.id.farm_house_icon);
                    apartment_icon.setImageResource(R.drawable.farm_house_colorful);
                } else {
                    farm_house_selected = false;
                    apartment_icon = findViewById(R.id.farm_house_icon);
                    apartment_icon.setImageResource(R.drawable.farm_house_black_and_white);
                }
                break;
            case R.id.serviced_apartment_icon:
                if (!serviced_apartment_selected) {
                    serviced_apartment_selected = true;
                    apartment_icon = findViewById(R.id.serviced_apartment_icon);
                    apartment_icon.setImageResource(R.drawable.serviced_apartment_colorful);
                } else {
                    serviced_apartment_selected = false;
                    apartment_icon = findViewById(R.id.serviced_apartment_icon);
                    apartment_icon.setImageResource(R.drawable.serviced_apartment_black_and_white);
                }
                break;
        }
        
        
    }
    
    public void offer_property_next_1(View view) {
        
        SQLiteManager mSQLiteManager = new SQLiteManager(getSqLiteDatabase());
        List queryResult = mSQLiteManager.retrieveFromDB("Property");
        ArrayList<PropertyTableObject> possibleMatches = new ArrayList<>();
        GetDistanceBetweenPoints getDistanceBetweenPoints = new GetDistanceBetweenPoints();
        
        for (Object object : queryResult) {
            
            if (!(object instanceof String)) {
                break;
            }
            
            PropertyTableObject tableObject = SharedResources.gson.fromJson(object.toString(), PropertyTableObject.class);
            
            if (!tableObject.getUuid().equals(ExecutionVariables.uuid)) {
                
                double distanceBetweenUserDestAndOfferedSrc = getDistanceBetweenPoints.getDistanceBetweenTwoPlaces(
                        tableObject.getSource_lat(), tableObject.getSource_lng(), srcLatLng.latitude, srcLatLng.longitude);
                
                if (distanceBetweenUserDestAndOfferedSrc < 10 && distanceBetweenUserDestAndOfferedSrc != Integer.MIN_VALUE) {
                    possibleMatches.add(tableObject);
                }
            }
        }
        
        if (possibleMatches.size() > 0) {
            
            Toast.makeText(getApplicationContext(), "Loading", Toast.LENGTH_SHORT).show();
            
            Intent intent = new Intent(getApplicationContext(), OfferPropertyMatchesScreen.class);
            
            Bundle matchesBundle = new Bundle();
            matchesBundle.putSerializable("objects", possibleMatches);
            
            intent.putExtra(getString(R.string.matches_intent_key), matchesBundle);
            startActivity(intent);
        } else {
            Toast.makeText(getApplicationContext(), "No matches found.", Toast.LENGTH_SHORT).show();
        }
        
    }
    
}
