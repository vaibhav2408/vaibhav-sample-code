package com.example.vaibhav.byob;

import android.content.Intent;
import android.database.sqlite.SQLiteDatabase;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.Menu;
import android.view.MenuItem;
import android.view.WindowManager;
import android.widget.Toast;

import com.example.vaibhav.byob.utils.sql.manager.SQLiteManager;
import com.google.android.material.bottomnavigation.BottomNavigationView;
import com.google.android.material.navigation.NavigationView;

import java.util.Objects;

import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;
import androidx.core.content.res.ResourcesCompat;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

public abstract class BaseActivity extends AppCompatActivity implements BottomNavigationView.OnNavigationItemSelectedListener, NavigationView.OnNavigationItemSelectedListener {
    
    protected BottomNavigationView bottomNavigationView;
    protected SQLiteDatabase sqLiteDatabase;
    protected boolean establishedDB = true;
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(getContentViewId());
        
        if (establishedDB) {
            setUpDB();
        }
        
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
        getWindow().setFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN,
                WindowManager.LayoutParams.FLAG_FULLSCREEN);
        
        loadElements();
        
        try {
            Objects.requireNonNull(getSupportActionBar()).hide();
        } catch (Exception ignored) {
        }
        
        bottomNavigationView = findViewById(R.id.navigation);
        bottomNavigationView.setOnNavigationItemSelectedListener(this);
        
        Toolbar toolbar = findViewById(R.id.toolbar);
        
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        
        ActionBarDrawerToggle mDrawerToggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        
        mDrawerToggle.setDrawerIndicatorEnabled(false);
        Drawable drawable = ResourcesCompat.getDrawable(getResources(), R.drawable.ic_menu_black_24dp, null);
        mDrawerToggle.setHomeAsUpIndicator(drawable);
        mDrawerToggle.setToolbarNavigationClickListener(v -> {
            if (drawer.isDrawerVisible(GravityCompat.START)) {
                drawer.closeDrawer(GravityCompat.START);
            } else {
                drawer.openDrawer(GravityCompat.START);
            }
        });
        
        drawer.addDrawerListener(mDrawerToggle);
    
//        drawer.setLayoutParams(new DrawerLayout.LayoutParams(50, 50));
        
        mDrawerToggle.syncState();
        
        NavigationView drawerNavigationView = findViewById(R.id.nav_view);
        drawerNavigationView.setNavigationItemSelectedListener(this);
        
    }
    
    public void setUpDB() {
        sqLiteDatabase = this.openOrCreateDatabase("Properties", MODE_PRIVATE, null);
        SQLiteManager sqLiteManager = new SQLiteManager(sqLiteDatabase);
        sqLiteManager.createTable("CREATE TABLE IF NOT EXISTS Property (tableContent VARCHAR)");
        establishedDB = false;
    }
    
    @Override
    protected void onStart() {
        super.onStart();
        updateNavigationBarState();
    }
    
    // Remove inter-activity transition to avoid screen tossing on tapping bottom navigation items
    @Override
    public void onPause() {
        super.onPause();
        overridePendingTransition(0, 0);
    }
    
    @Override
    public void onBackPressed() {
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }
    
    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }
    
    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        int id = item.getItemId();
        
        //noinspection SimplifiableIfStatement
        if (id == R.id.action_settings) {
            return true;
        }
        
        return super.onOptionsItemSelected(item);
    }
    
    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        switch (item.getItemId()) {
            
            // BOTTOM navigation drawer control start
            case R.id.offer_property:
                Toast.makeText(getApplicationContext(), "Loading..",
                        Toast.LENGTH_SHORT).show();
                Intent offerPropertyIntent = new Intent(getApplicationContext(),
                        OfferPropertyActivity.class);
                startActivity(offerPropertyIntent);
                return true;
            
            case R.id.account_settings:
                Toast.makeText(getApplicationContext(), "Loading..",
                        Toast.LENGTH_SHORT).show();
                Intent requestPropertyIntent = new Intent(getApplicationContext(),
                        UserAccountSettings.class);
                startActivity(requestPropertyIntent);
                return true;
            
            case R.id.my_matches:
                Toast.makeText(getApplicationContext(), "Clicked", Toast.LENGTH_SHORT).
                        show();
                Intent searchPropertyIntent = new Intent(getApplicationContext(),
                        UserPossibleMatches.class);
                startActivity(searchPropertyIntent);
                return true;
            
            case R.id.property_search:
                Toast.makeText(getApplicationContext(), "Clicked", Toast.LENGTH_SHORT).
                        show();
                Intent sserPossibleMatchesIntent = new Intent(getApplicationContext(),
                        SearchProperties.class);
                startActivity(sserPossibleMatchesIntent);
                return true;
            // BOTTOM navigation drawer control end
            
            // TOP drawer control start
            case R.id.today_notifications:
                Toast.makeText(getApplicationContext(), "Clicked notifications", Toast.LENGTH_SHORT).show();
                break;
            case R.id.whatsapp_message:
                Toast.makeText(getApplicationContext(), "Clicked whatsapp message", Toast.LENGTH_SHORT).show();
                break;
            case R.id.today_special:
                Toast.makeText(getApplicationContext(), "Clicked today special", Toast.LENGTH_SHORT).show();
                break;
            case R.id.timer:
                Toast.makeText(getApplicationContext(), "Clicked timer", Toast.LENGTH_SHORT).show();
                break;
            case R.id.tic_tac:
                Toast.makeText(getApplicationContext(), "Clicked tic_tac", Toast.LENGTH_SHORT).show();
                break;
            case R.id.hicker_watch:
                Toast.makeText(getApplicationContext(), "Clicked hicker watch", Toast.LENGTH_SHORT).show();
                break;
            case R.id.logout:
                Intent selectedIntent = new Intent(getApplicationContext(), LoginActivity.class);
                finishAffinity();
                startActivity(selectedIntent);
                break;
            // TOP drawer control end
        }
        
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
    
    private void updateNavigationBarState() {
        int actionId = getNavigationMenuItemId();
        selectBottomNavigationBarItem(actionId);
    }
    
    void selectBottomNavigationBarItem(int itemId) {
        MenuItem item = bottomNavigationView.getMenu().findItem(itemId);
        item.setChecked(true);
    }
    
    abstract int getContentViewId();
    
    abstract int getNavigationMenuItemId();
    
    abstract void loadElements();
    
    public SQLiteDatabase getSqLiteDatabase() {
        return sqLiteDatabase;
    }
    
}
