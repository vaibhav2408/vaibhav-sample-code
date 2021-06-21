package com.example.vaibhav.byob.utils.sqlObject;

import java.io.Serializable;
import java.util.UUID;

public class PropertyTableObject implements Serializable {
    
    private Double destination_lng;
    private UUID uuid;
    private String offer_id;
    private String source_address;
    private Double source_lat;
    private Double source_lng;
    private String destination_address;
    private Double destination_lat;
    private int isApartmentSelected;
    private int isHouseVillaSelected;
    private int isStudioApartmentSelected;
    private int isFarmHouseSelected;
    private int isServiceApartmentSelected;
    private long epochTime;
    
    public void setEpochTime(long epochTime) {
        this.epochTime = epochTime;
    }
    
    public long getEpochTime() {
        return epochTime;
    }
    
    public void setIsApartmentSelected(int isApartmentSelected) {
        this.isApartmentSelected = isApartmentSelected;
    }
    
    public void setIsHouseVillaSelected(int isHouseVillaSelected) {
        this.isHouseVillaSelected = isHouseVillaSelected;
    }
    
    public int getIsStudioApartmentSelected() {
        return isStudioApartmentSelected;
    }
    
    public void setIsStudioApartmentSelected(int isStudioApartmentSelected) {
        this.isStudioApartmentSelected = isStudioApartmentSelected;
    }
    
    public int getIsFarmHouseSelected() {
        return isFarmHouseSelected;
    }
    
    public void setIsFarmHouseSelected(int isFarmHouseSelected) {
        this.isFarmHouseSelected = isFarmHouseSelected;
    }
    
    public int getIsServiceApartmentSelected() {
        return isServiceApartmentSelected;
    }
    
    public void setIsServiceApartmentSelected(int isServiceApartmentSelected) {
        this.isServiceApartmentSelected = isServiceApartmentSelected;
    }
    
    
    public UUID getUuid() {
        return uuid;
    }
    
    public void setUuid(UUID uuid) {
        if (uuid != null)
            this.uuid = uuid;
        else
            try {
                throw new Exception();
            } catch (Exception ignored) {
            }
    }
    
    public String getOffer_id() {
        return offer_id;
    }
    
    public void setOffer_id(String offer_id) {
        this.offer_id = offer_id;
    }
    
    public String getSource_address() {
        return source_address;
    }
    
    public void setSource_address(String source_address) {
        this.source_address = source_address;
    }
    
    public Double getSource_lat() {
        return source_lat;
    }
    
    public void setSource_lat(Double source_lat) {
        this.source_lat = source_lat;
    }
    
    public Double getSource_lng() {
        return source_lng;
    }
    
    public void setSource_lng(Double source_lng) {
        this.source_lng = source_lng;
    }
    
    public String getDestination_address() {
        return destination_address;
    }
    
    public void setDestination_address(String destination_address) {
        this.destination_address = destination_address;
    }
    
    public Double getDestination_lat() {
        return destination_lat;
    }
    
    public void setDestination_lat(Double destination_lat) {
        this.destination_lat = destination_lat;
    }
    
    public Double getDestination_lng() {
        return destination_lng;
    }
    
    public void setDestination_lng(Double destination_lng) {
        this.destination_lng = destination_lng;
    }
}