package com.example.vaibhav.byob;

import android.content.Intent;
import android.graphics.drawable.Drawable;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Toast;

import com.google.android.material.navigation.NavigationView;

import androidx.appcompat.app.ActionBarDrawerToggle;
import androidx.appcompat.widget.Toolbar;
import androidx.core.content.res.ResourcesCompat;
import androidx.core.view.GravityCompat;
import androidx.drawerlayout.widget.DrawerLayout;

public class UserAccountSettings extends BaseActivity implements NavigationView.OnNavigationItemSelectedListener {
    
    @Override
    int getContentViewId() {
        return R.layout.activity_user_account_settings;
    }
    
    @Override
    int getNavigationMenuItemId() {
        return R.id.account_settings;
    }
    
    @Override
    void loadElements() {
        
        setContentView(R.layout.activity_user_account_settings);
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
        mDrawerToggle.syncState();
        
        NavigationView navigationView = findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);
        
    }
    
    public void logout(View view) {
        Intent intent = new Intent(getApplicationContext(), LoginActivity.class);
        finishAffinity();
        startActivity(intent);
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
    
    public boolean onNavigationItemSelected(MenuItem item) {
        
        Intent selectedIntent = null;
        
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
                selectedIntent = new Intent(getApplicationContext(), LoginActivity.class);
                finishAffinity();
                startActivity(selectedIntent);
                break;
            // TOP drawer control end
        }
        
        DrawerLayout drawer = findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }
    
}
