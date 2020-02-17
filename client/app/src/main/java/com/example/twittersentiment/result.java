package com.example.twittersentiment;

import androidx.appcompat.app.AppCompatActivity;

import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.github.mikephil.charting.charts.PieChart;
import com.github.mikephil.charting.components.Description;
import com.github.mikephil.charting.components.Legend;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.PieData;
import com.github.mikephil.charting.data.PieDataSet;
import com.github.mikephil.charting.data.PieEntry;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.DecimalFormat;
import java.util.ArrayList;

public class result extends AppCompatActivity {


    private String TAG = "result";
    private  Integer minute;
    private String suburb;
    private Double hisAverage;
    private TextView hisText,realText,topicText;
    private ProgressBar hisBar, realBar;
    private PieChart piechart;




    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_result);
        Intent getIntent = getIntent();
        minute = getIntent.getIntExtra("minute",600);
        suburb = getIntent.getStringExtra("suburb");
        String topic = getIntent.getStringExtra("topic");
        hisAverage = getIntent.getDoubleExtra("history",0);
        Double realAverage = getIntent.getDoubleExtra("average",0.0);
        int[] count = getIntent.getIntArrayExtra("count");
        hisText = findViewById(R.id.hisAverge);
        hisBar = findViewById(R.id.hisBar);
        realText = findViewById(R.id.realAverage);
        realBar = findViewById(R.id.realBar);
        topicText = findViewById(R.id.topic);
        piechart = findViewById(R.id.pieChart);
        piechart.setNoDataText("");
//        topicText.setText(topic);
        hisText.setText(String.format("%.4f", hisAverage));
        hisBar.setProgress((int)((hisAverage+1.0)*50));
//        String history = getIntent.getStringExtra("history");
//        Log.d(TAG, "onCreate: "+history);
        TextView suburbName = findViewById(R.id.subName);
        suburbName.setText(suburb.split("'")[1]);
        realtimeResult(realAverage,count);

//        sendHisRequest();
        sendTopicRequest();




    }

//    public  void sendHisRequest(){
//        new Thread(new Runnable() {
//            @Override
//            public void run() {
//                try {
//                    URL historyURL = new URL("http://1926b0aa.jp.ngrok.io/stats/historic");
//                    JSONObject his_result =  getHttpConnection(historyURL);
//                    if(!his_result.isNull(suburb)) {
//                        JSONObject history = (JSONObject) his_result.get(suburb);
//                        hisAverage = Double.parseDouble(history.getString("avg"));
//                    }
//                    else{
//                        hisAverage = 0.0;
//                    }
//                    showResponse(hisAverage);
//
//                } catch (Exception e) {
//                    e.printStackTrace();
//                    Log.d(TAG, "run: "+e.getMessage());
//                }
//            }
//        }).start();
//    }
//
//
    public  void sendTopicRequest(){
        new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    String code = suburb.split("'")[3];
                    URL topicURL = new URL("http://1926b0aa.jp.ngrok.io/stats/realtime/topics/location/cache?code="+code+"&minute="+minute);
                    JSONObject topic_result = getHttpConnection(topicURL);
                    Log.d(TAG, "run: "+topic_result.toString());
                    if(!topic_result.isNull(code)){
                        JSONArray topTopics = (JSONArray) topic_result.get(code);
                        JSONArray topic = (JSONArray) topTopics.get(0);
                        showTopicResponse((JSONArray)topic.get(1));
                    }else{
                        NoTopic();
                    }
//                    JSONArray topic = (JSONArray)topic_result.get("top_topics");


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

    private void NoTopic(){
        runOnUiThread((new Runnable() {
            @Override
            public void run() {
                topicText.setText("No data");
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

//    private void showResponse(final Double hisAverage) {
//        runOnUiThread(new Runnable() {
//            @Override
//            public void run() {
//                try {
//                    hisText.setText(String.format("%.4f", hisAverage));
//                    hisBar.setProgress((int)((hisAverage+1.0)*50));
//                } catch (Exception e) {
//                    e.printStackTrace();
//                }
//            }
//        });
//    }

    private void showTopicResponse(final JSONArray topic) {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                try {
                    String topTopics = "";
                    for(int i =0; i<5& i<topic.length();i++){
                        topTopics = topTopics+topic.getString(i)+"\n";
                    }
                    topicText.setText(topTopics);

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        });
    }


    private void realtimeResult(final Double realAverage,final int[] count) {
        try {
            realText.setText(String.format("%.4f",realAverage));
            realBar.setProgress((int)((realAverage+1.0)*50));
            if(count[0]+count[1]+count[2]==0){
                piechart.setNoDataText("No Tweets");
            }
            else {
                piechart.setHoleRadius(50f);
                piechart.setTransparentCircleRadius(30f);
                piechart.setHoleColor(Color.TRANSPARENT);
                piechart.setDrawEntryLabels(false);
                Description label = new Description();
                label.setText("Number of Tweets");
                label.setTextSize(15);
                piechart.setDescription(label);
                piechart.setExtraOffsets(5, 5, 5, 5);
                ArrayList<PieEntry> yValues = new ArrayList<>();
                yValues.add(new PieEntry(count[0], "Positive Tweets"));
                yValues.add(new PieEntry(count[1], "Negative Tweets"));
                yValues.add(new PieEntry(count[2], "Neutral Tweets"));
                PieDataSet pieDataSet = new PieDataSet(yValues, "");
                ArrayList<Integer> colors = new ArrayList<Integer>();
                colors.add(Color.parseColor("#80FF5722"));
                colors.add(Color.parseColor("#8003A9F4"));
                colors.add(Color.parseColor("#80FFEB3B"));
                pieDataSet.setColors(colors);
                pieDataSet.setValueTextColor(Color.BLACK);
                pieDataSet.setValueTextSize(10);
                pieDataSet.setSliceSpace(1f);
                pieDataSet.setSliceSpace(0);
                PieData pieData = new PieData(pieDataSet);
                piechart.setData(pieData);
                Legend legend = piechart.getLegend();
                legend.setVerticalAlignment(Legend.LegendVerticalAlignment.TOP);
                legend.setHorizontalAlignment(Legend.LegendHorizontalAlignment.RIGHT);
                legend.setOrientation(Legend.LegendOrientation.VERTICAL);
                legend.setTextSize(10);
                legend.setTextColor(Color.BLACK);
                legend.setXEntrySpace(7f);
                legend.setYEntrySpace(5f);
                piechart.animateXY(1000, 1000);
            }

        } catch (Exception e) {
            e.printStackTrace();
        }
    }



}
