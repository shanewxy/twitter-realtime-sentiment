package com.example.twittersentiment;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class result extends AppCompatActivity {


    private String TAG = "result";
    private  Integer minute;
    private String suburb;
    private Double hisAverage, realAverage;
    private TextView hisText,realText,topicText;
    private ProgressBar hisBar, realBar;




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);
        Intent getIntent = getIntent();
        minute = getIntent.getIntExtra("minute",600);
        suburb = getIntent.getStringExtra("suburb");
        sendHttpRequest();
        hisText = findViewById(R.id.hisAverge);
        hisBar = findViewById(R.id.hisBar);
        realText = findViewById(R.id.realAverage);
        realBar = findViewById(R.id.realBar);
        topicText = findViewById(R.id.topic);


    }

    public  void sendHttpRequest(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    URL historyURL = new URL("http://1926b0aa.jp.ngrok.io/stats/historic");
                    URL realURL = new URL("http://1926b0aa.jp.ngrok.io/stats/realtime?minute="+minute);
                    URL topicURL = new URL("http://1926b0aa.jp.ngrok.io/stats/realtime/topics?minute="+minute);
                    JSONObject his_result =  getHttpConnection(historyURL);
                    JSONObject real_result  = getHttpConnection(realURL);
                    JSONObject topic_result = getHttpConnection(topicURL);
                    if(!his_result.isNull(suburb)) {
                        JSONObject history = (JSONObject) his_result.get(suburb);
                        hisAverage = Double.parseDouble(history.getString("avg"));
                    }
                    else{
                        hisAverage = 0.0;
                    }
                    if(!real_result.isNull(suburb)){
                        JSONObject realTime = (JSONObject) real_result.get(suburb);
                        realAverage = Double.parseDouble(realTime.getString("avg"));
                    }
                    else{
                        realAverage = 0.0;
                    }
                    JSONArray topic = (JSONArray)topic_result.get("top_topics");
                    JSONArray topTopics = (JSONArray) topic.get(0);
                    Log.d(TAG, "run: "+suburb);
                    Log.d(TAG, "run: get the http result"+ hisAverage.toString());
                    Log.d(TAG, "run: "+ realAverage.toString());
                    Log.d(TAG, "run2: "+ topTopics.toString());
                    showResponse(hisAverage,realAverage,(JSONArray)topTopics.get(1));

                } catch (Exception e) {
                    e.printStackTrace();
                    Log.d(TAG, "run: "+e.getMessage());
                }
            }
        }).start();
    }

    private JSONObject getHttpConnection(URL url){
        try {
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setRequestMethod("GET");
            connection.connect();
            int responseCode = connection.getResponseCode();
            if(responseCode == HttpURLConnection.HTTP_OK  ){
                InputStream input = connection.getInputStream();
                JSONObject result =  getJsonObject(input);
                connection.disconnect();
                return result;
            }
            else{
                networkError();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return null;

    }


    private void networkError(){
        runOnUiThread((new Runnable() {
            @Override
            public void run() {
                Toast.makeText(result.this,"Network Error",Toast.LENGTH_SHORT);
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

    private void showResponse(final Double hisAverage, final Double realAverage, final JSONArray topic) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {

                    hisText.setText(String.valueOf(hisAverage));
                    hisBar.setProgress((int)(hisAverage+1)*50);
                    realText.setText(String.valueOf(realAverage));
                    realBar.setProgress((int)(realAverage+1)*50);
                    String topTopics = "";
                    for(int i =0; i<5;i++){
                        topTopics = topTopics+topic.getString(i)+"\n";
                    }
                    topicText.setText(topTopics);


                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }
}
