package com.example.vaibhav.byob.utils;

import com.example.vaibhav.byob.utils.gson.EscapeStringSerializer;
import com.google.gson.Gson;
import com.google.gson.GsonBuilder;

import java.security.SecureRandom;
import java.util.UUID;

import static java.lang.Math.floor;

public class SharedResources {
    
    public static final Gson gson = new GsonBuilder().registerTypeAdapter(String.class, new EscapeStringSerializer()).setLenient().create();
    
    public static final Gson gsonWithoutStringEscape = new GsonBuilder().setLenient().create();
    
    public static final Gson gsonWithoutHtmlEscaping = new GsonBuilder().disableHtmlEscaping().setLenient().create();
    
    public static final Gson gsonWithoutNullEscaping = new GsonBuilder().serializeNulls().create();
    
    private static SecureRandom rnd = new SecureRandom();
    
    public static String generateRandomString(int len) {
        String AB = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
        StringBuilder sb = new StringBuilder(len);
        for (int i = 0; i < len; i++) {
            sb.append(AB.charAt(rnd.nextInt(AB.length())));
        }
        return sb.toString();
    }
    
    public static String generateRandomString(String format) {
        try {
            return generateRandomString(Integer.parseInt(format));
        } catch (Exception e) {
            StringBuilder sb = new StringBuilder(format.length());
            for (char digit : format.toCharArray()) {
                if (digit == 'A') {
                    sb.append(getRandomAlphabet());
                } else if (digit == 'D') {
                    sb.append(getRandomDigit());
                }
            }
            return sb.toString();
        }
    }
    
    private static char getRandomAlphabet() {
        String AB = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
        return AB.charAt(rnd.nextInt(AB.length()));
    }
    
    public static char getRandomDigit() {
        String AB = "0123456789";
        return AB.charAt(rnd.nextInt(AB.length()));
    }
    
    public static long getRandom10Digits() {
        return (long) floor(Math.random() * 9_000_000_000L) +
                1_000_000_000L;
    }
    
    public static String generateRandomStringWithSuffix(String suffix) {
        StringBuilder sb = new StringBuilder(suffix.length());
        sb.append(generateRandomString(9)).append(suffix);
        return sb.toString();
    }
    
    public static UUID generateUUID() {
        return UUID.randomUUID();
    }
    
    
}
