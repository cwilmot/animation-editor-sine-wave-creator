# Corey Wilmot
# Sine Wave Editor
# 11-19-2014

import maya.cmds as cmds
import math

# Creates a pop-up window allowing the user to add a
# sine wave motion curve to selected, keyable attributes

class Sine_Window( object ):
    def __init__( self ):
        self.window = None
        self.window_name = 'sine_wave_window'
        self.title = "Sine Wave Creator"
        self.width = 300
        self.height = 350

    # Initialize new window, delete old one if it already exists
    def create(self):
        self.destroy()
        self.window = cmds.window(
            self.window_name       ,
            title    = self.title  ,
            width    = self.width  ,
            height   = self.height ,
            mnb      = False       ,
            mxb      = False       ,
            sizeable = False
            )
        
        # Add elements in the window
        self.create_list()
        self.create_fields_and_widgets()
        self.create_common_buttons()
        self.populate_attr_list()
        
        cmds.showWindow()


    def destroy( self ):
        if cmds.window( self.window_name, exists=True ):
            cmds.deleteUI( self.window_name, window=True )


    # Display the attribute textbox
    def create_list( self ):
        cmds.columnLayout( adj=True, columnAlign="center" )
        cmds.separator( height=10, style="none" )
        cmds.text( "object_selected_name", label="Keyable Attributes of: " )
        cmds.separator( height=3, style="none" )
        cmds.textScrollList( "attr_list", numberOfRows=8, height=100, allowMultiSelection=True )
        cmds.separator( height=15, style="none" )


    # Initialize textfields and sliders for the user to tweak
    def create_fields_and_widgets( self ):
        cmds.setParent("..")
        cmds.rowLayout( numberOfColumns=5 )

        cmds.text( label="Start Frame" )
        cmds.intField( "start_frame_textfield", value=int( cmds.playbackOptions( query=True, minTime=True ) ) )

        cmds.text( label="End Frame" )
        cmds.intField( "end_frame_textfield", value=int( cmds.playbackOptions( query=True, maxTime=True ) ) )
        
        cmds.setParent("..")
        cmds.columnLayout( )

        cmds.separator( height=15, style="none" )

        cmds.intSliderGrp( "wavelength_slider", label="Wavelength", min=1, max=100, fieldMaxValue=1000, field=True, value=10 )
        cmds.intSliderGrp( "phase_slider", label="Phase", min=0, max=360, field=True, value=0 )
        cmds.intSliderGrp( "amplitude_slider", label="Amplitude", min=1, max=100, fieldMinValue=-1000, fieldMaxValue=1000, field=True, value=5 )
        cmds.intSliderGrp( "offset_slider", label="Offset", min=-100, max=100, fieldMinValue=-1000, fieldMaxValue=1000, field=True, value=0 )
        cmds.separator( height=15, style="none" )


    # Initialize buttons
    def create_common_buttons( self ):
        cmds.setParent("..")
        cmds.rowLayout( numberOfColumns=2 )
        self.button_all_clear = cmds.button( label="Clear Attribute Keys", width=150, command=self.clear_all_button )
        self.button_clear = cmds.button( label="Clear Section Keys", width=150, command=self.clear_section_button )

        cmds.setParent("..")
        cmds.columnLayout( )
        cmds.separator( height=10, style="none" )

        cmds.setParent("..")
        cmds.rowLayout( numberOfColumns=4 )
        self.button_reset = cmds.button( label="Reset", width=75, command=self.reset_button )
        self.button_ref = cmds.button( label="Refresh", width=75, command=self.refresh_button )
        self.button_gen = cmds.button( label="Generate", width=75, command=self.gen_button )
        self.button_close = cmds.button( label="Close", width=75, command=self.close_button )
    

    # Fill in the attribute textbox with the selected object's keyable attributes.
    # If more than one object is selected, choose the last selected.
    # Remove attributes if nothing is selected.
    def populate_attr_list( self ):
        self.selected_object = cmds.ls( selection=True )

        if( len(self.selected_object) == 0 ):
            print "Nothing selected"
            cmds.text( "object_selected_name", label="Keyable Attributes of: ", edit=True )
            cmds.textScrollList( "attr_list", removeAll=True, height=100, edit=True )
        else:
            cmds.text( "object_selected_name", label="Keyable Attributes of: " + self.selected_object[len(self.selected_object)-1], edit=True )
            cmds.textScrollList( "attr_list", removeAll=True, edit=True )
            self.keyable_attributes = cmds.listAttr( self.selected_object[len(self.selected_object)-1], unlocked=True, keyable=True )
            cmds.textScrollList( "attr_list", append=self.keyable_attributes, edit=True )


    def create_sine_wave( self ):
        last_object = self.selected_object[len(self.selected_object)-1]
        self.attribute = cmds.textScrollList( "attr_list", selectItem=True, query=True )[0]
        self.start_frame = cmds.intField( "start_frame_textfield", value=True, query=True )
        self.end_frame = cmds.intField( "end_frame_textfield", value=True, query=True )
        self.wavelength = cmds.intSliderGrp( "wavelength_slider", value=True, query=True )
        self.phase = cmds.intSliderGrp( "phase_slider", value=True, query=True )
        self.amplitude = cmds.intSliderGrp( "amplitude_slider", value=True, query=True )
        self.offset = cmds.intSliderGrp( "offset_slider", value=True, query=True )

        self.phase = math.radians( self.phase )
        self.ang_frequency = ( 2 * math.pi ) / self.wavelength

        if( self.start_frame >= self.end_frame ):
            cmds.confirmDialog( message = "Your start frame is greater then your end frame.", button="Shame")
            return


        # Calculate the sine wave here and make keyframes on each frame.
        for x in range( self.start_frame - 1, self.end_frame + 2 ):
            y = self.amplitude*( math.sin( self.ang_frequency*( x-self.start_frame ) + self.phase ) ) + self.offset
            cmds.setKeyframe( last_object, time=x, attribute=self.attribute, value=y )
        
        # To create smooth tangents at the beginning and ending frames,
        # I made an extra keyframe before the starting frame and after the end frame
        # Then saved the in and out tangents on the end keframe
        # Deleted the extra keyframes at the beginning and the end
        # And finally replaced the tangents on the end keyframe with the ones we saved.
        tan_in = cmds.keyTangent( last_object, inAngle=True, time=( self.end_frame, self.end_frame ), query=True )[0]
        tan_out = cmds.keyTangent( last_object, outAngle=True, time=( self.end_frame, self.end_frame ), query=True )[0]
        cmds.cutKey( last_object, time=( self.start_frame-1, self.start_frame-1 ), attribute=self.attribute )
        cmds.cutKey( last_object, time=( self.end_frame+1, self.end_frame+1 ), attribute=self.attribute )
        cmds.keyTangent( last_object, inAngle=tan_in, outAngle=tan_out, time=( self.end_frame, self.end_frame ), attribute=self.attribute, edit=True )
    

    # The Clear Attribute Keys button removes all the keys from that selected attribute
    def clear_all_button( self, *args ):
        self.attribute = cmds.textScrollList( "attr_list", selectItem=True, query=True )

        if( self.attribute == None ):
            print "No attribute selected"
        else:
            cmds.cutKey( self.selected_object[len(self.selected_object)-1], clear=True, attribute=self.attribute )


    # The Clear Section Keys button removes all the keys between the start and end frame parameters
    def clear_section_button( self, *args ):
        self.attribute = cmds.textScrollList( "attr_list", selectItem=True, query=True )
        self.start_frame = int( cmds.intField( "start_frame_textfield", value=True, query=True ) )
        self.end_frame = int( cmds.intField( "end_frame_textfield", value=True, query=True ) )

        if( self.attribute == None ):
            print "No attribute selected"
        else:
            cmds.cutKey( self.selected_object[len(self.selected_object)-1], time=( self.start_frame, self.end_frame ), attribute=self.attribute )
     
                   
    # The Reset button puts default values back to the sliders and and text fields
    def reset_button( self, *args ):
        cmds.intField( "start_frame_textfield", value=int( cmds.playbackOptions( query=True, minTime=True ) ), edit=True )

        cmds.intField( "end_frame_textfield", value=int( cmds.playbackOptions( query=True, maxTime=True ) ), edit=True )

        cmds.intSliderGrp( "wavelength_slider", min=1, max=100, fieldMaxValue=1000, value=10, edit=True )

        cmds.intSliderGrp( "phase_slider", min=0, max=360, value=0, edit=True )

        cmds.intSliderGrp( "amplitude_slider", min=1, max=100, fieldMaxValue=1000, value=5, edit=True )

        cmds.intSliderGrp( "offset_slider", min=-100, max=100, fieldMinValue=-1000, fieldMaxValue=1000, value=0, edit=True )

    
    # The Refresh button updates the attribute list of the currently selected object
    def refresh_button( self, *args ):
        self.populate_attr_list()
        
    # The Generate button makes the sine wave for the selected attribute
    def gen_button( self, *args ):
        self.attribute = cmds.textScrollList( "attr_list", selectItem=True, query=True )

        if( self.attribute == None ):
            print "No attribute selected"
        else:
            self.create_sine_wave()
        
    # The Close button destroys the Sine Wave Creator window
    def close_button( self, *args ):
        self.destroy()
        
our_sine_window = Sine_Window()
our_sine_window.create()