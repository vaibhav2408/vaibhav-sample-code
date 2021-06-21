package com.example.vaibhav.byob.utils.sql.manager;

import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteStatement;

import java.util.ArrayList;
import java.util.List;

public class SQLiteManager {
    
    private SQLiteDatabase mDatabase;
    
    public SQLiteManager(SQLiteDatabase database) {
        this.mDatabase = database;
    }
    
    public void createTable(String query) {
        mDatabase.execSQL(query);
    }
    
    public void deleteTable(String tableName) {
        mDatabase.execSQL("DROP TABLE IF EXISTS " + tableName);
    }
    
    public void insertIntoDB(String query, String parameters) {
        
        SQLiteStatement statement = mDatabase.compileStatement(query);
        statement.bindString(1, parameters);
        
        statement.execute();
        
    }
    
    public List<Object> retrieveFromDB(String tableName) {
        
        List<Object> tableObjectArrayList = new ArrayList<>();
        
        try (Cursor cursor = mDatabase.rawQuery("select * from " + tableName, null)) {
            if (cursor.moveToFirst()) {
                while (!cursor.isAfterLast()) {
                    
                    String objectJSON = (cursor.getString(0));
                    
                    tableObjectArrayList.add(objectJSON);
                    cursor.moveToNext();
                }
            }
        }
        
        return tableObjectArrayList;
        
    }
    
    public List<Object> retrieveCustomValuesFromDB(String query) {
        
        List<Object> tableObjectArrayList = new ArrayList<>();
        
        try (Cursor cursor = mDatabase.rawQuery(query, null)) {
            if (cursor.moveToFirst()) {
                while (!cursor.isAfterLast()) {
                    
                    String objectJSON = (cursor.getString(0));
                    
                    tableObjectArrayList.add(objectJSON);
                    cursor.moveToNext();
                }
            }
        }
        
        return tableObjectArrayList;
        
    }
    
}
