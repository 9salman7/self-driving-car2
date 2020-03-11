#include<LiquidCrystal.h>

const int rs = 12, en = 11, d4 = A5, d5 = A4, d6 = A3, d7 = A2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);

const int EnableL = 5;
const int HighL = 6;       // LEFT SIDE MOTOR
const int LowL =7;

const int EnableR = 10;
const int HighR = 8;       //RIGHT SIDE MOTOR
const int LowR =9;

const int D0 = 1;       //Raspberry pin 24    LSB
const int D1 = 2;       //Raspberry pin 23
const int D2 = 3;       //Raspberry pin 22
const int D3 = 4;       //Raspberry pin 21    MSB

int a,b,c,d,data;

int time = 50;

void setup() {
	pinMode(EnableL, OUTPUT);      
	pinMode(HighL, OUTPUT);
	pinMode(LowL, OUTPUT);

	pinMode(EnableR, OUTPUT);
	pinMode(HighR, OUTPUT);
	pinMode(LowR, OUTPUT);

	pinMode(D0, INPUT_PULLUP);
	pinMode(D1, INPUT_PULLUP);
	pinMode(D2, INPUT_PULLUP);
	pinMode(D3, INPUT_PULLUP);

  lcd.begin(16, 2);

}

void forward()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,190);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,190);
 // delay(time);
}

void backward()
{
	digitalWrite(HighL, LOW);
	digitalWrite(LowL, HIGH);
	analogWrite(EnableL,255);

	digitalWrite(HighR, LOW);
	digitalWrite(LowR, HIGH);
	analogWrite(EnableR,255);
	//delay(time);
}

void Stop()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,0);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,0);
}

void forwardLeft()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,190);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,65);
	//delay(time);
}

void left()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,255);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,0);
	//delay(time);
}

void forwardRight()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,90);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,255);   
	//delay(time);
}

void right()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,0);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,230);
	//delay(time);   
}

void getData()
{
	 a = digitalRead(D0);
	 b = digitalRead(D1);
	 c = digitalRead(D2);
	 d = digitalRead(D3);
	 data = 8*d+4*c+2*b+a;
}

void loop(){
	getData();
	switch(data){
		case 1: forward(); 
		        lcd.print("Frwd");
		        break;
		case 2: backward();
            lcd.print("Rvrse");
		        break;
		case 3: right();
            lcd.print("Right");
		        break;
		case 4: left();
            lcd.print("Left");
		        break;
		case 5: forwardRight();
            lcd.print("FRight");
            break;
		case 6: forwardLeft(); 
            lcd.print("FLeft");
		        break;
		default: Stop();
            lcd.print("Stop");
		        break;
		
	}
}
