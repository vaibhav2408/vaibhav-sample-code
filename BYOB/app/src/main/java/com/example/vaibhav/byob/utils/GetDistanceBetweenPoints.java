package com.example.vaibhav.byob.utils;

import android.location.Location;

import java.text.DecimalFormat;

public class GetDistanceBetweenPoints {
    
    public double getDistanceBetweenTwoPlaces(double src_lat, double src_lng, double dest_lat, double dest_lng) {
        DecimalFormat df = new DecimalFormat("#.##");
        
        if (src_lat != 0.0 && src_lng != 0.0) {
            float[] result = new float[2];
            Location.distanceBetween(src_lat, src_lng, dest_lat, dest_lng, result);
            return Double.parseDouble(df.format(result[0] / 1000));
        } else {
            return Integer.MIN_VALUE;
        }
    }
    
}
