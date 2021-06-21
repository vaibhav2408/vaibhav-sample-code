package com.example.vaibhav.byob;

import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.os.Bundle;
import android.view.View;
import android.view.WindowManager;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.Toast;

import com.example.vaibhav.byob.utils.SharedResources;
import com.example.vaibhav.byob.utils.execution.variables.ExecutionVariables;
import com.example.vaibhav.byob.utils.sql.manager.SQLiteManager;
import com.example.vaibhav.byob.utils.sqlObject.UserTableObject;

import java.util.List;
import java.util.Objects;

import androidx.appcompat.app.AppCompatActivity;

public class LoginActivity extends AppCompatActivity {
    
    private EditText username;
    private EditText password;
    
    protected SQLiteDatabase sqLiteDatabase;
    protected SQLiteManager mSQSqLiteManager;
    private Switch userLoginRegistrationSwitch;
    
    List<Object> retrievedObjectArrayList;
    
    public void loginOrRegisterUser(View view) {
        
        String usernameValue = username.getText().toString();
        String passwordValue = password.getText().toString();
        
        boolean registerUser = false;
        
        if (usernameValue.equals("")) {
            Toast.makeText(getApplicationContext(), "Please enter both username and password.", Toast.LENGTH_SHORT).show();
        } else {
            
            if (userLoginRegistrationSwitch.isChecked()) {
                registerUser = true;
            }
            
            boolean isUserAlreadyCreated = checkIfUserExists(usernameValue);
            if (registerUser) {
                
                if (isUserAlreadyCreated) {
                    Toast.makeText(getApplicationContext(), "Username is already taken, please type a different one.", Toast.LENGTH_LONG).show();
                    clearTextFields();
                } else {
                    boolean userSuccessFullyCreated = registerNewUser(usernameValue, passwordValue);
                    if (userSuccessFullyCreated) {
                        Toast.makeText(getApplicationContext(), "User create successfully. \n Username - " + username.getText().toString(), Toast.LENGTH_LONG).show();
                        Intent intent = new Intent(getApplicationContext(), OfferPropertyActivity.class);
                        startActivity(intent);
                    } else {
                        Toast.makeText(getApplicationContext(), "User registration failed. Please re-try or contact us.", Toast.LENGTH_LONG).show();
                    }
                }
                
            } else {
                if (!isUserAlreadyCreated) {
                    Toast.makeText(getApplicationContext(), "Username doesn't exist. Please sign-up", Toast.LENGTH_LONG).show();
                    clearTextFields();
                } else {
                    boolean isCredentialCorrect = checkCredentials(usernameValue, passwordValue);
                    if (isCredentialCorrect) {
                        Toast.makeText(getApplicationContext(), "Login successful", Toast.LENGTH_LONG).show();
                        
                        Intent intent = new Intent(getApplicationContext(), OfferPropertyActivity.class);
                        startActivity(intent);
                    } else {
                        Toast.makeText(getApplicationContext(), "Username and password didn't match. Please check and try again.", Toast.LENGTH_LONG).show();
                        clearTextFields();
                    }
                }
            }
        }
    }
    
    public void clearTextFields() {
        username.setText("");
        password.setText("");
    }
    
    public boolean checkCredentials(String username, String password) {
        
        if (retrievedObjectArrayList == null) {
            mSQSqLiteManager = new SQLiteManager(sqLiteDatabase);
            String query = "SELECT * FROM " + getString(R.string.userTableName);
            retrievedObjectArrayList = mSQSqLiteManager.retrieveCustomValuesFromDB(query);
        }
        
        for (Object object : retrievedObjectArrayList) {
            if (!(object instanceof String)) {
                break;
            }
            UserTableObject mUserTableObject = SharedResources.gson.fromJson(object.toString(), UserTableObject.class);
            if (mUserTableObject.getUsername().equalsIgnoreCase(username) && mUserTableObject.getPassword().equals(password)) {
                
                ExecutionVariables.uuid = mUserTableObject.getUuid();
                ExecutionVariables.accountId = mUserTableObject.getAccountId();
                ExecutionVariables.username = mUserTableObject.getUsername();
                
                return true;
            }
        }
        
        return false;
        
    }
    
    public boolean checkIfUserExists(String usernameValue) {
        
        mSQSqLiteManager = new SQLiteManager(sqLiteDatabase);
        String query = "SELECT * FROM " + getString(R.string.userTableName);
        retrievedObjectArrayList = mSQSqLiteManager.retrieveCustomValuesFromDB(query);
        
        if (retrievedObjectArrayList.size() == 0) {
            return false;
        }
        
        for (Object object : retrievedObjectArrayList) {
            if (!(object instanceof String)) {
                break;
            }
            UserTableObject mUserTableObject = SharedResources.gson.fromJson(object.toString(), UserTableObject.class);
            if (mUserTableObject.getUsername().equalsIgnoreCase(usernameValue)) {
                return true;
            }
        }
        return false;
        
    }
    
    public boolean registerNewUser(String username, String password) {
        try {
            UserTableObject mUserTableObject = new UserTableObject(username, password);
            
            String userTableEntry = SharedResources.gson.toJson(mUserTableObject);
            String createUserQuery = "INSERT INTO " + getString(R.string.userTableName) + "(userInfoObject) VALUES(?)";
            
            mSQSqLiteManager.insertIntoDB(createUserQuery, userTableEntry);
            return true;
        } catch (Exception ignored) {
            return false;
        }
    }
    
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
        
        username = findViewById(R.id.username_input);
        password = findViewById(R.id.password_input);
        userLoginRegistrationSwitch = findViewById(R.id.userTypeSwitch);
        
        setUpDB();
    }
    
    protected void setUpDB() {
        sqLiteDatabase = this.openOrCreateDatabase("Users", MODE_PRIVATE, null);
        sqLiteDatabase.execSQL("CREATE TABLE IF NOT EXISTS " + getString(R.string.userTableName) + "(userInfoObject VARCHAR)");
    }
    
    boolean shouldAllowBack = false;
    int count = 0;
    
    @Override
    public void onBackPressed() {
        count += 1;
        if (!shouldAllowBack) {
            if (count > 1) {
                finish();
            }
            Toast.makeText(getApplicationContext(), "Press one more time to exit the application.", Toast.LENGTH_SHORT).show();
        } else {
            super.onBackPressed();
        }
    }
    
}
