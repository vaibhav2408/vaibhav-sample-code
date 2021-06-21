package com.example.vaibhav.byob;

import android.content.Intent;
import android.database.sqlite.SQLiteStatement;
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
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
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

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;

public class OfferPropertyActivity extends BaseActivity implements
        GoogleApiClient.OnConnectionFailedListener,
        GoogleApiClient.ConnectionCallbacks {
    
    private static final String TAG = OfferPropertyActivity.class.getSimpleName();
    
    private boolean apartment_selected = false;
    private boolean house_villa_selected = false;
    private boolean studio_apartment_selected = false;
    private boolean farm_house_selected = false;
    private boolean serviced_apartment_selected = false;
    
    private EditText dest_input_search;
    private EditText src_input_search;
    
    private LatLng srcLatLng;
    private LatLng destLatLng;
    
    private EditText mEditText;
    
    private static final int AUTOCOMPLETE_REQUEST_CODE = 22;
    
    
    @Override
    int getContentViewId() {
        return R.layout.activity_offer_property;
    }
    
    @Override
    int getNavigationMenuItemId() {
        return R.id.offer_property;
    }
    
    @Override
    public void onConnected(@Nullable Bundle bundle) {
    
    }
    
    @Override
    public void onConnectionSuspended(int i) {
    
    }
    
    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {
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
        
        findUsersMatches();
        
    }
    
    public void swapAddressValues(View view) {
        
        String tempAddressHolder = src_input_search.getText().toString();
        src_input_search.setText(dest_input_search.getText());
        dest_input_search.setText(tempAddressHolder);
        
        LatLng tempLatLngHolder = srcLatLng;
        srcLatLng = destLatLng;
        destLatLng = tempLatLngHolder;
        
        Toast.makeText(getApplicationContext(), "Swapped the addresses", Toast.LENGTH_SHORT).show();
    }
    
    @Override
    void loadElements() {
        
        Places.initialize(getApplicationContext(), getString(R.string.google_maps_API_Key));
        
        src_input_search = findViewById(R.id.src_input_search);
        dest_input_search = findViewById(R.id.dest_input_search);
        
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
                
                String address = place.getAddress();
                LatLng latLng = place.getLatLng();
                mEditText.setText(address);
                if (mEditText.getId() == src_input_search.getId()) {
                    srcLatLng = latLng;
                } else if (mEditText.getId() == dest_input_search.getId()) {
                    destLatLng = latLng;
                }
                
                
            } else if (resultCode == AutocompleteActivity.RESULT_ERROR) {
                Status status = Autocomplete.getStatusFromIntent(data);
                Log.i(TAG, status.getStatusMessage());
            } else if (resultCode == RESULT_CANCELED) {
                // The user canceled the operation.
                Toast.makeText(getApplicationContext(), "Search cancelled.", Toast.LENGTH_SHORT).show();
            }
        }
    }
    
    public void findUsersMatches() {
        
        double user_src_lat = srcLatLng.latitude;
        double user_src_lng = srcLatLng.longitude;
        double user_dest_lat = destLatLng.latitude;
        double user_dest_lng = destLatLng.longitude;
        
        GetDistanceBetweenPoints getDistanceBetweenPoints = new GetDistanceBetweenPoints();
        
        double distance = getDistanceBetweenPoints.getDistanceBetweenTwoPlaces(
                user_src_lat,
                user_src_lng,
                user_dest_lat,
                user_dest_lng);
        
        if (distance != Integer.MIN_VALUE) {
            Toast.makeText(getApplicationContext(), String.valueOf(distance) + "KM", Toast.LENGTH_SHORT).show();
        } else {
            Toast.makeText(getApplicationContext(), "Please check the addresses.", Toast.LENGTH_SHORT).show();
        }
        
        String source_address = src_input_search.getText().toString();
        String destination_address = dest_input_search.getText().toString();
        
        SQLiteManager sqLiteManager = new SQLiteManager(getSqLiteDatabase());
        
        List tableResults = sqLiteManager.retrieveFromDB("Property");
        
        ArrayList<PropertyTableObject> possibleMatches = new ArrayList<>();
        
        for (Object object : tableResults) {
            
            if (!(object instanceof String)) {
                break;
            }
            
            PropertyTableObject tableObject = SharedResources.gson.fromJson(object.toString(), PropertyTableObject.class);
            
            if (!tableObject.getUuid().equals(ExecutionVariables.uuid)) {
                
                double distanceBetweenUserSrcAndOfferedDest = getDistanceBetweenPoints.getDistanceBetweenTwoPlaces(
                        user_src_lat, user_src_lng, tableObject.getDestination_lat(), tableObject.getDestination_lng());
                
                double distanceBetweenUserDestAndOfferedSrc = getDistanceBetweenPoints.getDistanceBetweenTwoPlaces(
                        tableObject.getSource_lat(), tableObject.getSource_lng(), user_dest_lat, user_dest_lng);
                
                if (distanceBetweenUserSrcAndOfferedDest < 10 && distanceBetweenUserSrcAndOfferedDest != Integer.MIN_VALUE && distanceBetweenUserDestAndOfferedSrc < 10 && distanceBetweenUserDestAndOfferedSrc != Integer.MIN_VALUE) {
                    possibleMatches.add(tableObject);
                }
            }
        }
        
        //Inserting the latest into the DB
        try {
            PropertyTableObject tableObject = new PropertyTableObject();
            
            tableObject.setUuid(ExecutionVariables.uuid);
            tableObject.setOffer_id(SharedResources.generateRandomString(10));
            tableObject.setSource_address(source_address);
            tableObject.setDestination_address(destination_address);
            tableObject.setSource_lat(srcLatLng.latitude);
            tableObject.setSource_lng(srcLatLng.longitude);
            tableObject.setDestination_lat(destLatLng.latitude);
            tableObject.setDestination_lng(destLatLng.longitude);
            tableObject.setIsApartmentSelected(apartment_selected ? 1 : 0);
            tableObject.setIsHouseVillaSelected(house_villa_selected ? 1 : 0);
            tableObject.setIsStudioApartmentSelected(studio_apartment_selected ? 1 : 0);
            tableObject.setIsFarmHouseSelected(farm_house_selected ? 1 : 0);
            tableObject.setIsServiceApartmentSelected(serviced_apartment_selected ? 1 : 0);
            tableObject.setEpochTime(System.currentTimeMillis() / 1000);
            
            String query = "INSERT INTO Property (tableContent) VALUES(?)";
            SQLiteStatement statement = getSqLiteDatabase().compileStatement(query);
            statement.bindString(1, SharedResources.gson.toJson(tableObject));
            statement.execute();
            
        } finally {
            if (possibleMatches.size() > 0) {
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
    
}
