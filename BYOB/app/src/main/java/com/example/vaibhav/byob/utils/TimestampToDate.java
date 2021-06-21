package com.example.vaibhav.byob.utils;

import android.annotation.SuppressLint;

import java.text.SimpleDateFormat;
import java.util.Date;

public class TimestampToDate {
    
    public String epoch2DateString(long epochSeconds, String formatString) {
        Date updatedate = new Date(epochSeconds * 1000);
        @SuppressLint("SimpleDateFormat")
        SimpleDateFormat format = new SimpleDateFormat(formatString);
        return format.format(updatedate);
    }
    
}
