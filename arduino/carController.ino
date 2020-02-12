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
}

void forward()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,255);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,255);
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

void stop()
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
	analogWrite(EnableL,90);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,255);
	//delay(time);
}

void left()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,50);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,255);
	//delay(time);
}

void forwardRight()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,255);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,90);   
	//delay(time);
}

void right()
{
	digitalWrite(HighL, HIGH);
	digitalWrite(LowL, LOW);
	analogWrite(EnableL,255);

	digitalWrite(HighR, HIGH);
	digitalWrite(LowR, LOW);
	analogWrite(EnableR,50);
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
		case 1: forward(); break;
		case 2: backward(); break;
		case 3: right(); break;
		case 4: left(); break;
		case 5: forwardRight(); break;
		case 6: forwardLeft(); break;
		case 0: Stop(); break;
		
	}
}
