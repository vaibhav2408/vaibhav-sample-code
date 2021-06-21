package com.example.vaibhav.byob.utils.custom.adapters;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import com.example.vaibhav.byob.R;

import java.util.List;

public class MyListAdapter extends ArrayAdapter<String> {
    
    private final Activity context;
    private final List<String> address;
    private final List<String> offerId;
    private final List<String> date;
    
    public MyListAdapter(Activity context, List<String> date, List<String> offerId, List<String> address) {
        
        super(context, R.layout.custom_list_view, date);
        // TODO Auto-generated constructor stub
        
        this.context = context;
        this.address = address;
        this.offerId = offerId;
        this.date = date;
        
    }
    
    public View getView(int position, View view, ViewGroup parent) {
        LayoutInflater inflater = context.getLayoutInflater();
        
        @SuppressLint("ViewHolder")
        View rowView = inflater.inflate(R.layout.custom_list_view, null, true);
        
        TextView timeOfQuery = rowView.findViewById(R.id.timeOfQuery);
        TextView titleText = rowView.findViewById(R.id.title);
        TextView subtitleText = rowView.findViewById(R.id.subtitle);
        
        timeOfQuery.setText(date.get(position));
        titleText.setText(offerId.get(position));
        subtitleText.setText(address.get(position));
        
        return rowView;
    }
}