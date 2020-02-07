package com.example.twittersentiment;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.Resources;
import android.graphics.Color;
import android.location.Address;
import android.location.Geocoder;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.AutoCompleteTextView;
import android.widget.Button;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.maps.android.data.Feature;
import com.google.maps.android.data.geojson.GeoJsonFeature;
import com.google.maps.android.data.geojson.GeoJsonLayer;
import com.google.maps.android.data.geojson.GeoJsonPolygonStyle;


import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.List;

public class location extends AppCompatActivity implements OnMapReadyCallback,
        GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener,
        GoogleMap.OnMarkerClickListener, LocationListener {

    private GoogleMap mMap;
    private LocationManager locationManager;
    private String locationProvider,suburbName;
    private static final int LOCATION_CODE = 1;
    private Location mLastLocation;
    private String TAG = "location";
    private Button locationSearch;
    private AutoCompleteTextView sa2Name;
    private int time;
    private boolean flag;


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_location);
        // Obtain the SupportMapFragment and get notified when the map is ready to be used.
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                    .findFragmentById(R.id.map);
        locationSearch = findViewById(R.id.search);
        sa2Name = findViewById(R.id.locationName);
        Intent getIntent = getIntent();
        time = getIntent.getIntExtra("minute",1440);

        // the autoCompeleteTextView
        Resources resources = getResources();
        String[] name = resources.getStringArray(R.array.sa2NameArray);
        ArrayAdapter<String> adapter = new ArrayAdapter<String>(this,android.R.layout.simple_dropdown_item_1line,name);
        sa2Name.setAdapter(adapter);



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
                        mMap.animateCamera(CameraUpdateFactory.newLatLngZoom(latlng,12f));
                        Log.d(TAG, "onLocationChanged: new latlng");
                        try {
                            suburbName = getSuburb(location);
                            Log.d(TAG, "onMapReady: "+suburbName);
                        } catch (IOException e) {
                            e.printStackTrace();
                        }


                    }
                };

                locationManager.requestLocationUpdates(locationProvider,3000, 1,locationListener);
                mapFragment.getMapAsync(this);
                sendHttpRequest();



            }
        }catch(Exception e){
                Log.d(TAG, "onCreate: " + e);
        }
    }


    private void enterResponse(final JSONObject real_result) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    locationSearch.setOnClickListener(new View.OnClickListener() {
                        public void onClick(View v){
                            Log.d(TAG, "onClick: search button clicked");
                            try {
                                String enteredSuburbName;
                                Intent intent = new Intent(location.this, result.class);
                                if (!sa2Name.getText().toString().equals("")) {
                                    String enteredName = sa2Name.getText().toString();
                                    enteredSuburbName = getQueryName(enteredName);
                                } else {
                                    enteredSuburbName = suburbName;
                                }
                                intent.putExtra("suburb", enteredSuburbName);
                                if (!real_result.isNull(enteredSuburbName)) {
                                    JSONObject realTime = (JSONObject) real_result.get(enteredSuburbName);
                                    intent.putExtra("average", Double.parseDouble(realTime.getString("avg")));
                                    String pos = realTime.getString("positive");
                                    Log.d(TAG, "onFeatureClick: "+pos);
                                    int[] count = new int[]{Integer.parseInt(realTime.getString("positive")),
                                            Integer.parseInt(realTime.getString("negative")),
                                            Integer.parseInt(realTime.getString("neutral"))};
                                    intent.putExtra("count", count);
                                }else {
                                    int[] count = new int[]{0,0,0};
                                    intent.putExtra("average",0.0);
                                    intent.putExtra("count", count);
                                }
                                intent.putExtra("minute", time);
                                startActivity(intent);
                            }catch (Exception e){
                                Log.d(TAG, "onClick: "+e.getMessage());
                            }
                        }
                    });


                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
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
        try {
            mMap = googleMap;
            mMap.setMyLocationEnabled(true);
            Log.d(TAG, "onMapReady: Map ready");
            if(mLastLocation != null) {
                LatLng latlng = new LatLng(mLastLocation.getLatitude(), mLastLocation.getLongitude());
                mMap.moveCamera(CameraUpdateFactory.newLatLngZoom(latlng, 12f));
                suburbName = getSuburb(mLastLocation);



            }

        } catch (Exception e) {
            Log.d(TAG, "onMapReady: e: " + e);
        }
    }

    // convert the location to suburb name and SA2 code
    public String getSuburb(Location location) throws IOException {
        Geocoder addressCoder = new Geocoder(this);
        List address = addressCoder.getFromLocation(location.getLatitude(),location.getLongitude(),1);
        Address suburb = (Address) address.get(0);
        String name = suburb.getLocality();
        try {
            InputStreamReader is = new InputStreamReader(getResources().openRawResource(R.raw.locality_to_sa2));
            BufferedReader reader = new BufferedReader(is);
            reader.readLine();
            String line;
            while ((line = reader.readLine()) != null) {
                String item[] = line.split(",");
                if(name.equalsIgnoreCase(item[1])){
                    String code =  "2"+item[5].substring(item[5].length()-4);
                    return "('"+item[6]+"', '"+code+"')";
                }
            }
        } catch (IOException e) {
            Log.d(TAG, "getSuburb: "+e.getMessage());
        }

        return  null;
    }

    public String getQueryName(String enteredName){
        try {
            InputStreamReader is = new InputStreamReader(getResources().openRawResource(R.raw.code_sa2));
            BufferedReader reader = new BufferedReader(is);
            reader.readLine();
            String line;
            while ((line = reader.readLine()) != null) {
                String item[] = line.split(",");
                if(enteredName.equalsIgnoreCase(item[1])){
                    return "('"+item[1]+"', '"+item[0]+"')";
                }
            }
        } catch (IOException e) {
            Log.d(TAG, "getSuburb: "+e.getMessage());
        }

        return  null;

    }







    @Override
    public void onLocationChanged(Location location) {

    }

    @Override
    public void onStatusChanged(String s, int i, Bundle bundle) {

    }

    @Override
    public void onProviderEnabled(String s) {

    }

    @Override
    public void onProviderDisabled(String s) {

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

    @Override
    public boolean onMarkerClick(Marker marker) {
        return false;
    }

    public  void sendHttpRequest(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL realURL = new URL("http://1926b0aa.jp.ngrok.io/stats/realtime?minute=" + time);
                    getHttpConnection(realURL);
                } catch (IOException e) {
                    e.printStackTrace();
                    Log.d(TAG, "run: " + e.getMessage());
                } catch (Exception e) {
                    e.printStackTrace();
                    Log.d(TAG, "run: " + e.getMessage());
                }
            }

        }).start();
    }

    private void showMapResult(final JSONObject real_result){
        runOnUiThread(new  Runnable(){
            public void run(){
                try {
                    GeoJsonLayer layer = new GeoJsonLayer(mMap, R.raw.victoria,getApplicationContext());
                    GeoJsonPolygonStyle polygonStyle = layer.getDefaultPolygonStyle();
                    polygonStyle.setClickable(true);
                    polygonStyle.setStrokeColor(Color.BLUE);
                    polygonStyle.setStrokeWidth(2);
                    Log.d(TAG, "run: "+real_result);
                    if(real_result!=null) {
                        for (GeoJsonFeature feature : layer.getFeatures()) {
                            String name = "('" + feature.getProperty("SA2_NAME16") + "', '" + feature.getProperty("SA2_5DIG16") + "')";
                            GeoJsonPolygonStyle style = new GeoJsonPolygonStyle();
                            style.setStrokeColor(Color.BLUE);
                            style.setStrokeWidth(2);
                            style.setClickable(true);
                            if (!real_result.isNull(name)) {
                                Log.d(TAG, "onClick: " + name);
                                JSONObject realTime = (JSONObject) real_result.get(name);
                                float average = Float.parseFloat(realTime.getString("avg"));
                                int[] color = new int[]{251,211,211};
                                if (average > 0.0) {
                                    color[1] = color[1]- (int)(average*160);
                                    color[2] = color[2]- (int)(average*160);
                                }else if(average ==0){
                                    color[1] = 252;
                                    color[0] = 254;
                                }else {
                                    color[2] = 250;
                                    color[1] = color[1]+ (int)(average*160);
                                    color[0] = color[0]+ (int)(average*160)-60;
                                }
                                style.setFillColor(Color.rgb(color[0],color[1],color[2]));
                                feature.setPolygonStyle(style);
                            }else{
                                style.setFillColor(Color.WHITE);
                                feature.setPolygonStyle(style);
                            }
                        }
                    }
                    layer.addLayerToMap();
                    layer.setOnFeatureClickListener(new GeoJsonLayer.GeoJsonOnFeatureClickListener() {
                        @Override
                        public void onFeatureClick(Feature feature) {
                            try {
                                Intent intent = new Intent(location.this,result.class);
                                String name = "('" + feature.getProperty("SA2_NAME16") + "', '" + feature.getProperty("SA2_5DIG16") + "')";
                                intent.putExtra("suburb",name);
                                if (!real_result.isNull(name)) {
                                    JSONObject realTime = (JSONObject) real_result.get(name);
                                    intent.putExtra("average", Double.parseDouble(realTime.getString("avg")));
                                    String pos = realTime.getString("positive");
                                    Log.d(TAG, "onFeatureClick: "+pos);
                                    int[] count = new int[]{Integer.parseInt(realTime.getString("positive")),
                                            Integer.parseInt(realTime.getString("negative")),
                                            Integer.parseInt(realTime.getString("neutral"))};
                                    intent.putExtra("count", count);
                                }else {
                                    int[] count = new int[]{0,0,0};
                                    intent.putExtra("average",0.0);
                                    intent.putExtra("count", count);
                                }
                                intent.putExtra("minute",time);
                                startActivity(intent);
                            } catch (JSONException e) {
                                e.printStackTrace();
                            }
                        }
                    });

                } catch (IOException e) {
                    e.printStackTrace();
                } catch (JSONException e) {
                    e.printStackTrace();
                }

            }
        });
    }



    private void networkError(){
        runOnUiThread((new Runnable() {
            @Override
            public void run() {
                Toast.makeText(location.this,"Network Error",Toast.LENGTH_SHORT);
                Log.d(TAG, "run: network error");
            }
        }));
    }




    //Returns a json object from an input stream
    private JSONObject getJsonObject(InputStream input){

        try {
            BufferedReader streamReader = new BufferedReader(new InputStreamReader(input, "UTF-8"));
            StringBuilder responseStrBuilder = new StringBuilder();
            String inputStr;
            while ((inputStr = streamReader.readLine()) != null)
                responseStrBuilder.append(inputStr);

            JSONObject jsonObject = new JSONObject(responseStrBuilder.toString());

            //returns the json object
            return jsonObject;

        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }

        //if something went wrong, return null
        return null;
    }

    private void getHttpConnection(URL url){
        try {
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.connect();
            int responseCode = connection.getResponseCode();
            if(responseCode == HttpURLConnection.HTTP_OK  ){
                InputStream input = connection.getInputStream();
                JSONObject result =  getJsonObject(input);
                showMapResult(result);
                enterResponse(result);
                connection.disconnect();
            }
            else{
                networkError();
            }
        } catch (IOException e) {
            e.printStackTrace();
            Log.d(TAG, "getHttpConnection: "+e.getMessage());
        }

    }
}
