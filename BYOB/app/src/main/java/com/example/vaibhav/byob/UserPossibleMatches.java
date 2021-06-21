package com.example.vaibhav.byob;

import android.content.Intent;
import android.os.Bundle;
import android.widget.ListView;
import android.widget.Toast;

import com.example.vaibhav.byob.utils.GetDistanceBetweenPoints;
import com.example.vaibhav.byob.utils.SharedResources;
import com.example.vaibhav.byob.utils.TimestampToDate;
import com.example.vaibhav.byob.utils.custom.adapters.PossibleMatchesAdapter;
import com.example.vaibhav.byob.utils.execution.variables.ExecutionVariables;
import com.example.vaibhav.byob.utils.sql.manager.SQLiteManager;
import com.example.vaibhav.byob.utils.sqlObject.PropertyTableObject;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

public class UserPossibleMatches extends BaseActivity {
    
    @Override
    int getContentViewId() {
        return R.layout.activity_user_possible_matches;
    }
    
    @Override
    int getNavigationMenuItemId() {
        return R.id.my_matches;
    }
    
    @Override
    void loadElements() {
        
        ListView matchedProperties = findViewById(R.id.userPossibleMatches);
        
        SQLiteManager sqLiteManager = new SQLiteManager(getSqLiteDatabase());
        
        List<Object> tableResults = sqLiteManager.retrieveFromDB("Property");
        
        List<PropertyTableObject> listedPropertiesByOtherUser = new LinkedList<>();
        List<PropertyTableObject> listedPropertiesByTheUser = new LinkedList<>();
        
        Map<String, String> dataContainer = new HashMap<>();
        
        for (Object tableObject : tableResults) {
            
            if (!(tableObject instanceof String)) {
                break;
            }
            
            PropertyTableObject propertyTableObject = SharedResources.gson.fromJson(tableObject.toString(), PropertyTableObject.class);
            if (propertyTableObject.getUuid() != null && propertyTableObject.getUuid().equals(ExecutionVariables.uuid)) {
                
                TimestampToDate timestampToDate = new TimestampToDate();
                String date = timestampToDate.epoch2DateString(propertyTableObject.getEpochTime(), "E-dd-MMM");
                String dateToBeDisplayed = "";
                String[] dateSplits = date.split("-");
                for (String dateSplit : dateSplits) {
                    dateToBeDisplayed += dateSplit + System.lineSeparator();
                }
                
                dataContainer.put(dateToBeDisplayed.substring(0, dateToBeDisplayed.lastIndexOf(System.lineSeparator())),
                        propertyTableObject.getOffer_id() + "__" + propertyTableObject.getSource_address());
                
                listedPropertiesByTheUser.add(propertyTableObject);
                
            } else
                listedPropertiesByOtherUser.add(propertyTableObject);
            
        }
        
        final List<String> date = new ArrayList<>();
        final List<String> offerId = new ArrayList<>();
        final List<String> address = new ArrayList<>();
        
        for (String key : dataContainer.keySet()) {
            date.add(key);
            String[] title_subtitleContent = dataContainer.get(key).split("__");
            
            offerId.add(title_subtitleContent[0]);
            address.add(title_subtitleContent[1]);
        }
        
        PossibleMatchesAdapter adapter = new PossibleMatchesAdapter(this, date, offerId, address);
        
        matchedProperties.setAdapter(adapter);
        
        matchedProperties.setOnItemClickListener((parent, view, position, id) -> {
            PropertyTableObject clickedObject = listedPropertiesByTheUser.get(position);
            
            GetDistanceBetweenPoints getDistanceBetweenPoints = new GetDistanceBetweenPoints();
            
            ArrayList<PropertyTableObject> possibleMatchesSrc = new ArrayList<>();
            
            for (PropertyTableObject object : listedPropertiesByOtherUser) {
                
                if (object.getOffer_id() != null && object.getUuid() != null &&
                        !object.getOffer_id().equals(clickedObject.getOffer_id()) &&
                        !object.getUuid().equals(clickedObject.getUuid())) {
                    
                    double distanceBetweenUserSrcAndOfferedDest = getDistanceBetweenPoints.getDistanceBetweenTwoPlaces(
                            object.getSource_lat(), object.getSource_lng(), clickedObject.getDestination_lat(), clickedObject.getDestination_lng());
                    
                    double distanceBetweenUserDestAndOfferedSrc = getDistanceBetweenPoints.getDistanceBetweenTwoPlaces(
                            clickedObject.getSource_lat(), clickedObject.getSource_lng(), object.getDestination_lat(), object.getDestination_lng());
                    
                    if (distanceBetweenUserSrcAndOfferedDest < 10 && distanceBetweenUserSrcAndOfferedDest != Integer.MIN_VALUE && distanceBetweenUserDestAndOfferedSrc < 10 && distanceBetweenUserDestAndOfferedSrc != Integer.MIN_VALUE) {
                        possibleMatchesSrc.add(object);
                        
                    }
                }
                
            }
            
            if (possibleMatchesSrc.size() > 0) {
                Intent intent = new Intent(UserPossibleMatches.this.getApplicationContext(), OfferPropertyMatchesScreen.class);
                
                Bundle matchesBundle = new Bundle();
                matchesBundle.putSerializable("objects", possibleMatchesSrc);
                
                intent.putExtra(UserPossibleMatches.this.getString(R.string.matches_intent_key), matchesBundle);
                UserPossibleMatches.this.startActivity(intent);
            } else {
                Toast.makeText(UserPossibleMatches.this.getApplicationContext(), "No possible matches found. Please come back later.", Toast.LENGTH_SHORT).show();
            }
            
        });
        
    }
    
}
