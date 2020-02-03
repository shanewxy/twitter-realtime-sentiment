package com.example.twittersentiment;

import androidx.core.app.ActivityCompat;
import androidx.fragment.app.FragmentActivity;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.MarkerOptions;

import java.io.IOException;
import java.util.List;

public class search extends FragmentActivity implements OnMapReadyCallback {

    private GoogleMap mMap;
    private LocationManager locationManager;
    private String locationProvider, suburbName;
    private static final int LOCATION_CODE = 1;
    private Location mLastLocation;
    private String TAG = "search";
    private Button search;
    private SeekBar timebar;
    private TextView showTime;
    private int time = 1440;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_search);
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        timebar = findViewById(R.id.Time);
        showTime = (TextView) findViewById(R.id.showTime);
        search = findViewById(R.id.button);

        timebar.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
            @Override
            public void onProgressChanged(SeekBar seekBar, int progress, boolean fromUser) {
                Log.i(TAG, "onProgressChanged=" + progress);
            }

            @Override
            public void onStartTrackingTouch(SeekBar seekBar) {
                Log.i(TAG, "onStartTrackingTouch=");
            }

            @Override
            public void onStopTrackingTouch(SeekBar seekBar) {
                int seekProgress = seekBar.getProgress();
                if (seekProgress == 0) {
                    time = 1; // 1 min
                    showTime.setText("Last 1 minute");
                } else if (seekProgress == 1) {
                    time = 10; // 10 mins
                    showTime.setText("Last 10 minute");
                } else if (seekProgress == 2) {
                    time = 60; // 1 hour
                    showTime.setText("Last 1 hour");
                } else if (seekProgress == 3) {
                    time = 60 * 24; // 1 day
                    showTime.setText("Last 1 day");
                } else if (seekProgress == 4) {
                    time = 60 * 24 * 7; // 1 week
                    showTime.setText("Last 1 week");
                } else if (seekProgress == 5) {
                    time = 60 * 24 * 7 * 2;
                    showTime.setText("Last 2 weeks");
                } else if (seekProgress == 6) {
                    time = 60 * 24 * 7 * 4;
                    showTime.setText("Last 1 month");
                }
                Log.i(TAG, "onStopTrackingTouch=");
            }
        });

        // listen the search button
        search.setOnClickListener(new View.OnClickListener() {
            public void onClick(View v){
                Log.d(TAG, "onClick: search button clicked");


                Intent intent = new Intent(search.this,location.class);
                intent.putExtra("minute",time);
                startActivity(intent);

            }
        });




        //  get the location permission
        try {
            if (ActivityCompat.checkSelfPermission(this,
                    android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]
                        {android.Manifest.permission.ACCESS_FINE_LOCATION}, LOCATION_CODE);

            } else {
                locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
                //obtain all the location providers
                List<String> providers = locationManager.getProviders(true);
                if (providers.contains(LocationManager.GPS_PROVIDER)) {
                    //GPS
                    locationProvider = LocationManager.GPS_PROVIDER;
                    Log.d(TAG, "Get the GPS provider!");
                } else if (providers.contains(LocationManager.NETWORK_PROVIDER)) {
                    //Network
                    locationProvider = LocationManager.NETWORK_PROVIDER;
                    Log.d(TAG, "Get the Network provider!");
                } else {
                    Toast.makeText(this, "no location provider", Toast.LENGTH_SHORT).show();
                }

                mLastLocation = locationManager.getLastKnownLocation(locationProvider);

                if (mLastLocation != null) {
                    Log.d(TAG, "bestProvider : get the location success!");
                } else {
                    Log.d(TAG, "bestProvider : get the location failed!");
                }
                //listen the location change
                LocationListener locationListener = new LocationListener() {

                    @Override
                    public void onStatusChanged(String provider, int status, Bundle arg2) {
                    }

                    @Override
                    public void onProviderEnabled(String provider) {
                    }

                    @Override
                    public void onProviderDisabled(String provider) {
                    }

                    @Override
                    public void onLocationChanged(Location location) {
                        LatLng latlng = new LatLng(location.getLatitude(), location.getLongitude());
                        mMap.animateCamera(CameraUpdateFactory.newLatLngZoom(latlng, 12f));
                        Log.d(TAG, "onLocationChanged: new latlng");

                    }
                };

                locationManager.requestLocationUpdates(locationProvider, 3000, 1, locationListener);
                mapFragment.getMapAsync(this);


            }
        } catch (Exception e) {
            Log.d(TAG, "onCreate: " + e);
        }
    }


    /**
     * Manipulates the map once available.
     * This callback is triggered when the map is ready to be used.
     * This is where we can add markers or lines, add listeners or move the camera. In this case,
     * we just add a marker near Sydney, Australia.
     * If Google Play services is not installed on the device, the user will be prompted to install
     * it inside the SupportMapFragment. This method will only be triggered once the user has
     * installed Google Play services and returned to the app.
     */
    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        mMap.setMyLocationEnabled(true);
        Log.d(TAG, "onMapReady: Map ready");
        if (mLastLocation != null) {
            LatLng latlng = new LatLng(mLastLocation.getLatitude(), mLastLocation.getLongitude());
            mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(latlng, 12f));

        }
    }
}
