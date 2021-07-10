#include <EloquentTinyML.h>

// copy the printed code from tinymlgen into this file
#include "ts_forecast_lite.h"

#define NUMBER_OF_INPUTS 6
#define NUMBER_OF_OUTPUTS 1
#define TENSOR_ARENA_SIZE 8*1024

Eloquent::TinyML::TfLite<NUMBER_OF_INPUTS, NUMBER_OF_OUTPUTS, TENSOR_ARENA_SIZE> ml;

void setup() {
    Serial.begin(115200);
    ml.begin(ts_forecast_lite);
}

void loop() {
    // a random sample from the dataset
    float x_test[6] = { 0.011838 , 0.011790 , 0.011750  , 0.011695, 0.011352, 0.012072 };
    //float x_test[6] = { 0.010249, 0.010063 , 0.010045 , 0.010524 , 0.011292  , 0.012596 };
    
    // the output vector for the model predictions
    float y_pred[1] = {};
    
    // the actual output of the sample
    float y_test = 0.011611; //actual 0.012330
    //float y_test = 0.012217; //actual 0.012260

    // let's see how long it takes to classify the sample
    uint32_t start = micros();

    ml.predict(x_test, y_pred);

    uint32_t timeit = micros() - start;

    Serial.print("It took ");
    Serial.print(timeit);
    Serial.println(" micros to run inference");

    // let's print the raw predictions for all the classes
    // these values are not directly interpretable as probabilities!
    Serial.print("Test output is: ");
    Serial.println(y_test, 7);
    Serial.print("Predicted value is: ");
    Serial.println(y_pred[1], 7);

/*
    // let's print the "most probable" class
    // you can either use probaToClass() if you also want to use all the probabilities
    Serial.print("Predicted value is: ");
    Serial.println(ml.probaToClass(y_pred));
    // or you can skip the predict() method and call directly predictClass()
    Serial.print("Sanity check: ");
    Serial.println(ml.predictClass(x_test));
*/

    delay(1000);
}
